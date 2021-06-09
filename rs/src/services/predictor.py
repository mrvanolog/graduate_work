import psycopg2
import pandas as pd

from recommender.recommender import Recommender
from recommender.collab_filter import CollabFilterRecommender
from conf.settings import sql_ratings, sql_movies, columns_ratings, columns_movies
from conf.settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD


class Predictor():
    def __init__(self, conn_data: psycopg2.connection, conn_predictions: psycopg2.connection):
        self.conn_data: psycopg2.connection = conn_data
        self.conn_predictions: psycopg2.connection = conn_predictions

        self.ratings: pd.DataFrame = self._get_ratings_data()
        self.movies: pd.DataFrame = self._get_movies_data()

        self.cf_rec: Recommender = CollabFilterRecommender(self.ratings, self.movies)

    def _get_ratings_data(self) -> pd.DataFrame:
        """Create DataFrame for ratings data from postgres.
        """
        with self.conn_data.cursor() as cur:
            cur.execute(sql_ratings)
            result = cur.fetchall()

        return pd.DataFrame(result, columns=columns_ratings)

    def _get_movies_data(self) -> pd.DataFrame:
        """Create DataFrame for movies data from postgres.
        """
        with self.conn_data.cursor() as cur:
            cur.execute(sql_movies)
            result = cur.fetchall()

        return pd.DataFrame(result, columns=columns_movies)

    def unpersonalised_recommendation(self):
        pass

    def predict_for_users(self):
        recommendations: dict = {}
        for user_id, group in self.ratings.groupby('user_id'):
            if group['user_id'].count() < 10:
                self.unpersonalised_recommendation()

            recommendations[user_id] = self.cf_rec.predict_for_user(user_id)

            # TODO: upload recommendations to rs-predictions

    def predict_for_movies(self):
        recommendations: dict = {}
        for movie_id, group in self.ratings.groupby('movie_id'):
            if group['movie_id'].count() < 10:
                self.unpersonalised_recommendation()

            recommendations[movie_id] = self.cf_rec.predict_for_movie(movie_id)

            # TODO: upload recommendations to rs-predictions


def get_predictor():
    conn_data = psycopg2.connect(f"""
        host={POSTGRES_HOST}
        port={POSTGRES_PORT}
        dbname=rs-data
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)
    conn_predictions = psycopg2.connect(f"""
        host={POSTGRES_HOST}
        port={POSTGRES_PORT}
        dbname=rs-predictions
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)
    return Predictor(conn_data, conn_predictions)
