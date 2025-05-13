import torch
import copy
import numpy as np
import math
from sklearn.model_selection import train_test_split
from torch import optim
from torch.nn import functional as F
from torch.optim.lr_scheduler import _LRScheduler

from .iterator import batches_train, batches_recommend


# Custom learning rate scheduler using a cyclic learning rate strategy
class CyclicLR(_LRScheduler):
    def __init__(self, optimizer, schedule, last_epoch=-1):
        assert callable(schedule)
        self.schedule = schedule
        super().__init__(optimizer, last_epoch)

    # Adjust learning rate based on the custom schedule
    def get_lr(self):
        return [self.schedule(self.last_epoch, lr) for lr in self.base_lrs]


# Cosine annealing schedule for cyclic learning rate
def cosine(t_max, eta_min=0):
    def scheduler(epoch, base_lr):
        t = epoch % t_max
        return eta_min + (base_lr - eta_min) * (1 + math.cos(math.pi * t / t_max)) / 2

    return scheduler


# Train the model with early stopping and cyclic learning rate
def train_model(net, X, y, n_epochs, lr, wd, bs, patience, minmax, device):
    # Split data into training and validation sets
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    datasets = {"train": (X_train, y_train), "val": (X_valid, y_valid)}
    dataset_sizes = {"train": len(X_train), "val": len(X_valid)}

    optimizer = optim.Adam(net.parameters(), lr=lr, weight_decay=wd)
    criterion = torch.nn.MSELoss(reduction="sum")
    iterations_per_epoch = int(math.ceil(dataset_sizes["train"] / bs))
    scheduler = CyclicLR(
        optimizer, cosine(t_max=iterations_per_epoch * 2, eta_min=lr / 10)
    )

    best_loss = np.inf
    best_weights = None
    no_improvements = 0
    history = []
    lr_history = []

    for epoch in range(n_epochs):
        stats = {"epoch": epoch + 1, "total": n_epochs}
        for phase in ("train", "val"):
            training = phase == "train"
            running_loss = 0.0
            n_batches = 0

            for batch in batches_train(*datasets[phase], shuffle=training, bs=bs):
                x_batch, y_batch = [b.to(device) for b in batch]
                user_ids = x_batch[:, 0]
                movie_ids = x_batch[:, 1]
                genres = x_batch[:, 2:]

                optimizer.zero_grad()
                with torch.set_grad_enabled(training):
                    outputs = net(user_ids, movie_ids, genres, minmax)
                    loss = criterion(outputs, y_batch)

                    if training:
                        loss.backward()
                        optimizer.step()
                        scheduler.step()
                        lr_history.extend(scheduler.get_lr())

                running_loss += loss.item()
                n_batches += 1

            epoch_loss = running_loss / dataset_sizes[phase]
            stats[phase] = epoch_loss

            # Check for improvement in validation loss
            if phase == "val":
                if epoch_loss < best_loss:
                    print(f"Loss improvement on epoch: {epoch + 1}")
                    best_loss = epoch_loss
                    best_weights = copy.deepcopy(net.state_dict())
                    no_improvements = 0
                else:
                    no_improvements += 1

        history.append(stats)
        print(
            "[{epoch:03d}/{total:03d}] train: {train:.4f} - val: {val:.4f}".format(
                **stats
            )
        )

        # Stop training if no improvement in validation loss
        if no_improvements >= patience:
            print("Early stopping after epoch {epoch:03d}".format(**stats))
            break

    # Load the best model weights
    net.load_state_dict(best_weights)
    return net, history, lr_history


# Update embedding layers with new user and movie indices
def update_embedding_layers(
    net, new_user_id, rated_movies, user_to_index, movie_to_index
):
    if new_user_id not in user_to_index:
        new_user_index = len(user_to_index)
        user_to_index[new_user_id] = new_user_index
        with torch.no_grad():
            net.u = torch.nn.Embedding(len(user_to_index), net.u.embedding_dim).to(
                net.u.weight.device
            )
            net.u.weight.data[-1] = torch.rand(net.u.embedding_dim) * 0.1 - 0.05

    if rated_movies is not None:
        for movie_id, _ in rated_movies:
            if movie_id not in movie_to_index:
                new_movie_index = len(movie_to_index)
                movie_to_index[movie_id] = new_movie_index
                with torch.no_grad():
                    net.m = torch.nn.Embedding(
                        len(movie_to_index), net.m.embedding_dim
                    ).to(net.m.weight.device)
                    net.m.weight.data[-1] = torch.rand(net.m.embedding_dim) * 0.1 - 0.05

    return user_to_index, movie_to_index


# Perform incremental learning with new user data
def incremental_learning(
    net,
    X,
    y,
    userID,
    rated_movies,
    user_to_index,
    movie_to_index,
    movies,
    genres_split,
    lr,
    wd,
    bs,
    minmax,
    device,
):
    # Split data into training and validation sets
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    dataset_sizes = {"train": len(X_train), "val": len(X_valid)}

    new_user_index = user_to_index[userID]
    X_new = []
    y_new = []
    genres_movie = movies["genres"].str.get_dummies(", ")
    movie_genres = movies[["movieId"]].join(genres_movie)

    # Prepare new user data for training
    for movie_id, rating in rated_movies:
        new_movie_index = movie_to_index[movie_id]
        genres_vector = (
            movie_genres[movie_genres["movieId"] == movie_id]
            .drop("movieId", axis=1)
            .values
        )
        if genres_vector.size > 0:
            genres_vector = genres_vector[0]
        else:
            genres_vector = np.zeros(len(genres_split.columns))
        X_new.append([new_user_index, new_movie_index] + genres_vector.tolist())
        y_new.append(rating)

    X_new = torch.tensor(X_new, dtype=torch.float32)
    y_new = torch.tensor(y_new, dtype=torch.float32)

    optimizer = optim.Adam(net.parameters(), lr=lr, weight_decay=wd)
    criterion = torch.nn.MSELoss(reduction="sum")
    iterations_per_epoch = int(math.ceil(dataset_sizes["train"] / bs))
    scheduler = CyclicLR(
        optimizer, cosine(t_max=iterations_per_epoch * 2, eta_min=lr / 10)
    )

    net.train()
    X_new = X_new.to(device)
    y_new = y_new.to(device)

    n_epochs_new = 20
    for epoch in range(n_epochs_new):
        stats = {"epoch": epoch + 1, "total": n_epochs_new}
        running_loss = 0.0
        n_batches = 0

        for batch in batches_recommend(X_new, y_new, shuffle=True, bs=bs):
            x_batch, y_batch = [b.to(device) for b in batch]
            user_ids = x_batch[:, 0]
            movie_ids = x_batch[:, 1]
            genres = x_batch[:, 2:]

            optimizer.zero_grad()
            with torch.set_grad_enabled(True):
                outputs = net(user_ids, movie_ids, genres, minmax)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()
                scheduler.step()

            running_loss += loss.item()
            n_batches += 1

        # Log training loss for each epoch
        epoch_loss = running_loss / len(X_new)
        stats["train"] = epoch_loss
        print("[{epoch:03d}/{total:03d}] train: {train:.4f}".format(**stats))

    print("Training with new data completed.")
    return net