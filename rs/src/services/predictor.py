from typing import List
import pandas as pd
import psycopg2.extras

from conf.settings import (POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT,
                           POSTGRES_USER, columns_movies, columns_ratings,
                           sql_delete_movies, sql_delete_users,
                           sql_insert_movies, sql_insert_users, sql_movies,
                           sql_ratings)
from recommender.collab_filter import CollabFilterRecommender
from recommender.recommender import Recommender

from rs.src.conf.settings import POSTGRES_DATA_DB, POSTGRES_PREDICTIONS_DB


class Predictor():
    def __init__(self, conn_data: psycopg2._connect, conn_predictions: psycopg2._connect):
        self.conn_data: psycopg2._connect = conn_data
        self.conn_predictions: psycopg2._connect = conn_predictions

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

    def unpersonalised_recommendation(self) -> list:
        """Return a list of movies by their average rating.
        """
        return self.movies.sort_values('rating', ascending=False)['id'].values.tolist()

    def predict_for_users(self):
        """Create predictions for each user and upload them to rs-predictions db.
        """
        recommendations: List[tuple] = []
        for user_id, group in self.ratings.groupby('user_id'):
            if group['user_id'].count() < 10:
                movies = self.unpersonalised_recommendation()
            movies = self.cf_rec.predict_for_user(user_id)

            recommendations.append((user_id, movies))

        with self.conn_predictions.cursor() as cur:
            # delete old predictions
            cur.execute(sql_delete_users)

            # add new predictions
            psycopg2.extras.execute_values(cur, sql_insert_users, recommendations)

        self.conn_predictions.commit()

    def predict_for_movies(self):
        """Create predictions for each movie and upload them to rs-predictions db.
        """
        recommendations: List[tuple] = []
        for movie_id, group in self.ratings.groupby('movie_id'):
            if group['movie_id'].count() < 10:
                movies = self.unpersonalised_recommendation()
            movies = self.cf_rec.predict_for_movie(movie_id)

            recommendations.append((movie_id, movies))

        with self.conn_predictions.cursor() as cur:
            # delete old predictions
            cur.execute(sql_delete_movies)

            # add new predictions
            psycopg2.extras.execute_values(cur, sql_insert_movies, recommendations)

        self.conn_predictions.commit()


def get_predictor():
    conn_data = psycopg2.connect(f"""
        host={POSTGRES_HOST}
        port={POSTGRES_PORT}
        dbname={POSTGRES_DATA_DB}
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)
    conn_predictions = psycopg2.connect(f"""
        host={POSTGRES_HOST}
        port={POSTGRES_PORT}
        dbname={POSTGRES_PREDICTIONS_DB}
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)

    return Predictor(conn_data, conn_predictions)
