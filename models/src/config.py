import pandas as pd
import torch

from .data import create_dataset_with_genres
from .model import EmbeddingNet

# Training parameters
lr = 1e-3
wd = 1e-5
bs = 2000
n_epochs = 100
patience = 10

# Model parameters
n_factors = 150
hidden_size = [500, 500, 500]
embedding_dropout = 0.05
dropouts = [0.5, 0.5, 0.25]

# Recommendation parameters
top_k = 10

# Load data
ratings = pd.read_csv("models/data/ratings.csv")
movies = pd.read_csv("models/data/movies.csv")
ratings = ratings.merge(movies[["movieId", "genres"]], on="movieId", how="left")
ratings = ratings.drop(["comment"], axis=1)
genres_split = ratings["genres"].str.get_dummies(", ")

# Create dataset
(n_users, n_movies, n_genres), (X, y), (user_to_index, movie_to_index) = (
    create_dataset_with_genres(ratings, genres_split)
)

# Initialize model
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

print(device)

net = EmbeddingNet(
    n_users,
    n_movies,
    n_genres,
    n_factors=n_factors,
    hidden=hidden_size,
    embedding_dropout=embedding_dropout,
    dropouts=dropouts,
)

net.to(device)

minmax = ratings.rating.min(), ratings.rating.max()