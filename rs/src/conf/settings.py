import os

# postgres
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

# SQL
sql_ratings = 'SELECT movie_id, user_id, rating FROM rs_data.ratings'
columns_ratings = ['movie_id', 'user_id', 'rating']
sql_movies = 'SELECT id, rating FROM rs_data.movies'
columns_movies = ['id', 'rating']
