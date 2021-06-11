import os

# postgres
POSTGRES_PREDICTIONS_DB = os.environ.get('POSTGRES_PREDICTIONS_DB')
POSTGRES_PREDICTIONS_HOST = os.environ.get('POSTGRES_PREDICTIONS_HOST')
POSTGRES_PREDICTIONS_PORT = os.environ.get('POSTGRES_PREDICTIONS_PORT')
POSTGRES_PREDICTIONS_USER = os.environ.get('POSTGRES_PREDICTIONS_USER')
POSTGRES_PREDICTIONS_PASSWORD = os.environ.get('POSTGRES_PREDICTIONS_PASSWORD')

POSTGRES_DATA_DB = os.environ.get('POSTGRES_DATA_DB')
POSTGRES_DATA_HOST = os.environ.get('POSTGRES_DATA_HOST')
POSTGRES_DATA_PORT = os.environ.get('POSTGRES_DATA_PORT')
POSTGRES_DATA_USER = os.environ.get('POSTGRES_DATA_USER')
POSTGRES_DATA_PASSWORD = os.environ.get('POSTGRES_DATA_PASSWORD')

# SQL
sql_ratings = 'SELECT movie_id, user_id, rating FROM rs_data.ratings'
columns_ratings = ['movie_id', 'user_id', 'rating']
sql_movies = 'SELECT id, rating FROM rs_data.movies'
columns_movies = ['id', 'rating']

sql_delete_users = 'DELETE FROM predictions.users'
sql_insert_users = """
INSERT INTO predictions.users (user_id, rec_movie_id)
VALUES %s
"""

sql_delete_movies = 'DELETE FROM predictions.movies'
sql_insert_movies = """
INSERT INTO predictions.movies (movie_id, rec_movie_id)
VALUES %s
"""
