import os

# postgres
POSTGRES_MOVIES_DB = os.environ.get('POSTGRES_MOVIES_DB')
POSTGRES_MOVIES_HOST = os.environ.get('POSTGRES_MOVIES_HOST')
POSTGRES_MOVIES_PORT = os.environ.get('POSTGRES_MOVIES_PORT')
POSTGRES_MOVIES_USER = os.environ.get('POSTGRES_MOVIES_USER')
POSTGRES_MOVIES_PASSWORD = os.environ.get('POSTGRES_MOVIES_PASSWORD')

POSTGRES_UGC_DB = os.environ.get('POSTGRES_UGC_DB')
POSTGRES_UGC_HOST = os.environ.get('POSTGRES_UGC_HOST')
POSTGRES_UGC_PORT = os.environ.get('POSTGRES_UGC_PORT')
POSTGRES_UGC_USER = os.environ.get('POSTGRES_UGC_USER')
POSTGRES_UGC_PASSWORD = os.environ.get('POSTGRES_UGC_PASSWORD')

POSTGRES_DATA_DB = os.environ.get('POSTGRES_DATA_DB')
POSTGRES_DATA_HOST = os.environ.get('POSTGRES_DATA_HOST')
POSTGRES_DATA_PORT = os.environ.get('POSTGRES_DATA_PORT')
POSTGRES_DATA_USER = os.environ.get('POSTGRES_DATA_USER')
POSTGRES_DATA_PASSWORD = os.environ.get('POSTGRES_DATA_PASSWORD')

SSL_MODE = os.environ.get('SSL_MODE')

# flush time
FLUSH_SECONDS = int(os.environ.get('FLUSH_SECONDS', default=1800))

# templates
columns_ratings = 'user_id, movie_id, rating, created_at'
columns_movies = """
    id,
    title,
    description,
    creation_date,
    certificate,
    file_path,
    rating,
    type,
    created_at,
    updated_at
"""

sql_insert_ratings = """
INSERT INTO rs_data.ratings (user_id, movie_id, rating, created_at)
VALUES %s
"""
sql_insert_movies = """
INSERT INTO rs_data.movies (id, title, rating, type, created_at, updated_at)
VALUES %s
"""
