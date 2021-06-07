import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine

from services.recommender import Recommender


class CollabFilterRecommender(Recommender):
    """Recommender class that produces predictions using collaborative filtration.
    """
    def __init__(self, ratings: pd.DataFrame, movies: pd.DataFrame):
        self.ratings: pd.DataFrame = ratings
        self.movies: pd.DataFrame = movies

        self.num_users: int = ratings['user_id'].unique().shape[0]
        self.num_movies: int = ratings['movie_id'].unique().shape[0]

        self.user_positions: dict = self._generate_positions(entity='user_id')
        self.movie_positions: dict = self._generate_positions(entity='movie_id')
        self.inverse_movie_positions: dict = self._generate_inverse_movie_positions()

    def _generate_positions(self, entity: str):
        """Prepare dictionary with a position in a vector for each entity.
        """
        positions = {}

        for i, val in enumerate(self.ratings[entity].unique()):
            positions[val] = i

        return positions

    def _generate_inverse_movie_positions(self):
        """Prepare dictionary with a movie_id of each position in a vector.
        """
        positions = {}

        for i, val in enumerate(self.ratings['movie_id'].unique()):
            positions[i] = val

        return positions

    def predict_for_movie(self, movie_id: str) -> list:
        """Find movies that are similar to the target movie.

        Args:
            movie_id (str): Target movie

        Returns:
            list: List of similar movies sorted by similarity, most simiilar movies
            are in the beginning of the list and the least similar are in the end
        """
        movie_vector = {}

        for movie, group in self.ratings.groupby('movie_id'):
            movie_vector[movie] = np.zeros(self.num_users)

            for i, user_id in enumerate(group['user_id'].values):
                u = self.user_positions[user_id]
                r = group['rating'].values[i]

                movie_vector[movie][int(u - 1)] = r

        movie_ids = []
        distances = []

        for key in movie_vector.keys():
            if key == movie_id:
                continue

            movie_ids.append(key)
            distances.append(cosine(movie_vector[movie_id], movie_vector[key]))

        best_indexes = np.argsort(distances)[:10]
        best_movies = [movie_ids[i] for i in best_indexes]

        return best_movies

    def predict_for_user(self, user_id: str) -> list:
        """Find movies that the most similar users have watched and the target user hasn't.

        Args:
            user_id (str): Target user

        Returns:
            list: List of movies from similar users sorted by average rating,
            movies with the highest rating are in the beginning of the list
            and movies with the lowest rating are in the end
        """
        user_vector = {}

        for user, group in self.ratings.groupby('user_id'):
            user_vector[user] = np.zeros(self.num_movies)

            for i, movie_id in enumerate(group['movie_id'].values):
                m = self.movie_positions[movie_id]
                r = group['rating'].values[i]

                user_vector[user][int(m - 1)] = r

        user_ids = []
        distances = []

        for key in user_vector.keys():
            if key == user_id:
                continue

            user_ids.append(key)
            distances.append(cosine(user_vector[user_id], user_vector[key]))

        best_indexes = np.argsort(distances)[:5]
        similar_users = [user_ids[i] for i in best_indexes]

        # search for movies that similar users watched and target user has not
        best_movies = []

        for i, movie in enumerate(user_vector[user_id]):
            if movie:
                continue

            for similar_user in similar_users:
                if user_vector[similar_user][i]:
                    best_movies.append(self.inverse_movie_positions[i])
                    break

        condition = self.movies['id'].isin(best_movies)
        best_movies_sorted = (
            self.movies[condition].sort_values('rating', ascending=False)['id'].values.tolist()
        )

        return best_movies_sorted
