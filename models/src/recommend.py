import os

import torch
import numpy as np
import pickle

from .train import update_embedding_layers, incremental_learning
from .config import *


def get_most_rated_movies(ratings, movies, top_k):
    # Calculate the global average rating (C) and the 90th percentile of the number of ratings per movie (m).
    C = ratings["rating"].mean()
    m = ratings["movieId"].value_counts().quantile(0.9)

    # Compute the number of ratings and average rating for each movie.
    movie_stats = (
        ratings.groupby("movieId")
        .agg(num_ratings=("rating", "count"), avg_rating=("rating", "mean"))
        .reset_index()
    )

    # Filter movies with a number of ratings greater than or equal to the 90th percentile (m).
    qualified_movies = movie_stats[movie_stats["num_ratings"] >= m]

    # Calculate a weighted rating for each qualified movie using a weighted average formula.
    qualified_movies["weighted_rating"] = (
        qualified_movies["num_ratings"] / (qualified_movies["num_ratings"] + m)
    ) * qualified_movies["avg_rating"] + (m / (m + qualified_movies["num_ratings"])) * C

    # Select the top-k movies with the highest weighted ratings.
    top_k_movies = qualified_movies.sort_values(
        "weighted_rating", ascending=False
    ).head(top_k)
    top_k_movieId = list(top_k_movies["movieId"])

    # Retrieve the titles of the top-k movies.
    top_movies_titles = [
        movies[movies.movieId == movieId]["title"].values[0]
        for movieId in top_k_movieId
    ]

    # Return the movieIds and titles of the top-k movies.
    return top_k_movieId, top_movies_titles


# Generate a list of recommended movies for a given user
def get_recommended_movies(
    model,
    userID,  # User ID for whom recommendations are generated
    ratings,  # Ratings data
    movies,  # Movies data
    genres_split,  # One-hot encoded genres
    user_to_index,  # Mapping from user IDs to indices
    movie_to_index,  # Mapping from movie IDs to indices
    top_k,  # Number of top recommendations to return
    device,  # Device to perform computations on
    rated_movies=None,  # Optional list of already rated movies
):
    # Prepare genre information for all movies
    genres_movie = movies["genres"].str.get_dummies(", ")
    movie_genres = movies[["movieId"]].join(genres_movie)
    user_index = user_to_index[userID]

    # Get all movies and those seen by the user
    all_movies = ratings["movieId"].unique()
    if rated_movies is None:
        seen_movies = ratings[ratings.userId == userID]["movieId"].unique()
    else:
        seen_movies = [movie for movie, _ in rated_movies]

    # Map movie IDs to indices
    all_movie_indices = [movie_to_index[movie] for movie in all_movies]
    seen_movie_indices = [movie_to_index[movie] for movie in seen_movies]

    # Identify movies not seen by the user
    unseen_movies = set(all_movie_indices) - set(seen_movie_indices)

    index_to_movie = {index: movie for movie, index in movie_to_index.items()}

    prediction_ratings = []
    for movie_index in unseen_movies:
        movie_tensor = torch.tensor([movie_index]).to(device)
        user_tensor = torch.tensor([user_index]).to(device)

        movie_id = index_to_movie[movie_index]
        genres_vector = (
            movie_genres[movie_genres["movieId"] == movie_id]
            .drop("movieId", axis=1)
            .values
        )

        # Handle cases where the genre vector might be empty
        if genres_vector.size > 0:
            genres_vector = genres_vector[0]
        else:
            genres_vector = np.zeros(len(genres_split.columns))

        genres_tensor = torch.tensor(genres_vector).unsqueeze(0).to(device).float()

        # Predict the rating for the unseen movie
        with torch.no_grad():
            prediction = model(user_tensor, movie_tensor, genres_tensor)
        prediction_ratings.append((movie_index, prediction.item()))

    # Sort predictions and get the top recommended movies
    prediction_ratings.sort(key=lambda x: x[1], reverse=True)
    top_movies = [movie_index for movie_index, _ in prediction_ratings[:top_k]]

    # Convert indices back to movie IDs and titles
    top_movies_movieId = [index_to_movie[movie_index] for movie_index in top_movies]
    top_movies_titles = [
        movies[movies.movieId == movieId]["title"].values[0]
        for movieId in top_movies_movieId
    ]

    return top_movies_movieId, top_movies_titles


def get_recommendations(userId, rated_movies, top_k=10):

    global net
    

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..' ))

    # # Xây dựng đường dẫn tuyệt đối đến file best.weights
    weights_path = os.path.join(project_root, 'checkpoints', 'best.weights')



    if rated_movies is None:
        top_movies_movieId, top_movies_titles = get_most_rated_movies(
            ratings, movies, top_k
        )
    else:


        # Load best model weights
        with open(weights_path, "rb") as dbfile:
            best_weights = pickle.load(dbfile)
            net.load_state_dict(best_weights)
            
        global user_to_index, movie_to_index    

        # Update embedding layers
        user_to_index, movie_to_index = update_embedding_layers(
            net, userId, rated_movies, user_to_index, movie_to_index
        )

        # Incremental learning
        net = incremental_learning(
            net,
            X,
            y,
            userId,
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

        # Recommend movies for the new user
        top_movies_movieId, top_movies_titles = get_recommended_movies(
            net,
            userId,
            ratings,
            movies,
            genres_split,
            user_to_index,
            movie_to_index,
            top_k,
            device,
            rated_movies,
        )

    return list(zip(top_movies_movieId, top_movies_titles))