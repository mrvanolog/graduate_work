import os

# postgres
# POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
# POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
# POSTGRES_USER = os.environ.get('POSTGRES_USER')
# POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_USER = 'user_admin'
POSTGRES_PASSWORD = 'qwerty123'
POSTGRES_HOST = 'rc1b-9g35diheb1pr3mvu.mdb.yandexcloud.net'
POSTGRES_PORT = 6432

# flush time
FLUSH_SECONDS = int(os.environ.get('FLUSH_SECONDS', default=5))

# templates
columns_ratings = 'movie_id, user_id, rating, created_at'
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
