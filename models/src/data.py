import numpy as np
import pandas as pd

def create_dataset_with_genres(ratings, genres_split, top=None):
    if top is not None:
        ratings.groupby("userId")["rating"].count()

    unique_users = ratings.userId.unique()
    user_to_index = {old: new for new, old in enumerate(unique_users)}
    new_users = ratings.userId.map(user_to_index)

    unique_movies = ratings.movieId.unique()
    movie_to_index = {old: new for new, old in enumerate(unique_movies)}
    new_movies = ratings.movieId.map(movie_to_index)

    n_users = unique_users.shape[0]
    n_movies = unique_movies.shape[0]

    X = pd.DataFrame({"user_id": new_users, "movie_id": new_movies})
    y = ratings["rating"].astype(np.float32)

    X = pd.concat([X, genres_split], axis=1)

    return (
        (n_users, n_movies, genres_split.shape[1]),
        (X, y),
        (user_to_index, movie_to_index),
    )