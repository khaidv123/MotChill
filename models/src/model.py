import torch
from torch import nn
from itertools import zip_longest


# Converts a number or an iterable to a list
def get_list(n):
    if isinstance(n, (int, float)):
        return [n]
    elif hasattr(n, "__iter__"):
        return list(n)
    raise TypeError(
        "layers configuration should be a single number or a list of numbers"
    )


# Neural network model for movie recommendation based on embeddings
class EmbeddingNet(nn.Module):
    def __init__(
        self,
        n_users,  # Number of unique users
        n_movies,  # Number of unique movies
        n_genres,  # Number of unique genres (one-hot encoded)
        n_factors=50,  # Embedding size for users and movies
        embedding_dropout=0.02,  # Dropout rate for embeddings
        hidden=10,  # Hidden layer configuration
        dropouts=0.2,  # Dropout rates for hidden layers
    ):
        super().__init__()

      
        hidden = get_list(hidden)
        dropouts = get_list(dropouts)
        n_last = hidden[-1]  


        def gen_layers(n_in):
            nonlocal hidden, dropouts
            assert len(dropouts) <= len(hidden)

            for n_out, rate in zip_longest(hidden, dropouts):
                yield nn.Linear(n_in, n_out)
                yield nn.ReLU()
                if rate is not None and rate > 0.0:
                    yield nn.Dropout(rate)
                n_in = n_out

        # User and movie embedding layers
        self.u = nn.Embedding(n_users, n_factors)
        self.m = nn.Embedding(n_movies, n_factors)
        self.drop = nn.Dropout(embedding_dropout)

        # Hidden layers with input size based on embeddings and genres
        n_input = n_factors * 2 + n_genres
        self.hidden = nn.Sequential(*list(gen_layers(n_input)))

        # Output layer
        self.fc = nn.Linear(n_last, 1)

        # Initialize model weights
        self._init()

    # Defines forward pass for the network
    def forward(self, users, movies, genres, minmax=None):
        # Compute user and movie embeddings
        user_embedding = self.u(users)
        movie_embedding = self.m(movies)

        # Concatenate embeddings and genres
        features = torch.cat([user_embedding, movie_embedding, genres], dim=1)

        # Apply dropout and pass through hidden layers
        x = self.drop(features)
        x = self.hidden(x)

        # Output prediction with sigmoid activation
        out = torch.sigmoid(self.fc(x))

        # Scale output if minmax provided
        if minmax is not None:
            min_rating, max_rating = minmax
            out = out * (max_rating - min_rating + 1) + min_rating - 0.5
        return out

    # Initializes weights for the model layers
    def _init(self):
        # Initialize weights for linear layers using Xavier initialization
        def init(m):
            if type(m) == nn.Linear:
                torch.nn.init.xavier_uniform_(m.weight)
                m.bias.data.fill_(0.01)

        # Initialize embedding layers
        self.u.weight.data.uniform_(-0.05, 0.05)
        self.m.weight.data.uniform_(-0.05, 0.05)

        # Apply initialization to hidden layers
        self.hidden.apply(init)
        init(self.fc)