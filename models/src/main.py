import pickle
from train import train_model, update_embedding_layers, incremental_learning
from recommend import get_recommended_movies, get_most_rated_movies
from .eval import eval_model
from .config import *

# inputs = 1 to train model and recommend movies for a user
# inputs = 2 to incremental learning and recommend movies for a new user
inputs = 1

if inputs == 1:
    # # Train model
    net, history, lr_history = train_model(
         net, X, y, n_epochs, lr, wd, bs, patience, minmax, device
    )

    final_loss = eval_model(net, X, y, bs, minmax, device)

    # # Save best model weights
    with open("checkpoints/best.weights", "wb") as file:
         pickle.dump(net.state_dict(), file)

    # Recommend movies for a user
    userID = 161
    top_movies_movieId, top_movies_titles = get_recommended_movies(
        net,
        userID,
        ratings,
        movies,
        genres_split,
        user_to_index,
        movie_to_index,
        top_k,
        device,
    )

    # Display recommended movies
    for movieId, movieTitle in zip(top_movies_movieId, top_movies_titles):
        print(f"{movieId}: {movieTitle}")

# Incremental learning and recommend movies for a new user
if inputs == 2:

    userID = 123456789
    rated_movies = [[31, 4.5]]

    if rated_movies is None:
        top_movies_movieId, top_movies_titles = get_most_rated_movies(
            ratings, movies, top_k
        )

    else:
        # Load best model weights
        with open("checkpoints/best.weights", "rb") as dbfile:
            best_weights = pickle.load(dbfile)
            net.load_state_dict(best_weights)

        # Update embedding layers
        user_to_index, movie_to_index = update_embedding_layers(
            net, userID, rated_movies, user_to_index, movie_to_index
        )

        # Incremental learning
        net = incremental_learning(
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
        )

        # Recommend movies for a new user
        top_movies_movieId, top_movies_titles = get_recommended_movies(
            net,
            userID,
            ratings,
            movies,
            genres_split,
            user_to_index,
            movie_to_index,
            top_k,
            device,
            rated_movies,
        )

    # Display recommended movies
    for movieId, movieTitle in zip(top_movies_movieId, top_movies_titles):
        print(f"{movieId}: {movieTitle}")