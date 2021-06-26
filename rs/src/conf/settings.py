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

SSL_MODE = os.environ.get('SSL_MODE')

# SQL
sql_ratings = f'SELECT movie_id, user_id, rating FROM "{POSTGRES_DATA_DB}".ratings'
columns_ratings = ['movie_id', 'user_id', 'rating']
sql_movies = f'SELECT id, rating FROM "{POSTGRES_DATA_DB}".movies'
columns_movies = ['id', 'rating']

sql_delete_users = f'DELETE FROM "{POSTGRES_PREDICTIONS_DB}".users'
sql_insert_users = f"""
INSERT INTO "{POSTGRES_PREDICTIONS_DB}.users" (user_id, rec_movie_id)
VALUES %s
"""

sql_delete_movies = f'DELETE FROM "{POSTGRES_PREDICTIONS_DB}".movies'
sql_insert_movies = f"""
INSERT INTO "{POSTGRES_PREDICTIONS_DB}".movies (movie_id, rec_movie_id)
VALUES %s
"""
