import os
from pathlib import Path
import psycopg2

POSTGRES_HOST = os.environ.get('POSTGRES_HOST',
                               default='rc1b-9g35diheb1pr3mvu.mdb.yandexcloud.net')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', default='6432')
POSTGRES_USER = os.environ.get('POSTGRES_USER', default='user_admin')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', default='qwerty123')
POSTGRES_MOVIES_DB = os.environ.get('POSTGRES_MOVIES_DB', default='content')
POSTGRES_USERS_DB = os.environ.get('POSTGRES_USERS_DB', default='users')
POSTGRES_UGC_DB = os.environ.get('POSTGRES_UGC_DB', default='ugc')
SSL_MODE = 'disable'

path_data = Path().cwd().joinpath('data')

path_film_work = path_data.joinpath('film_work.txt')
path_genre_film_work = path_data.joinpath('genre_film_work.txt')
path_genre = path_data.joinpath('genre.txt')
path_person_film_work = path_data.joinpath('person_film_work.txt')
path_person = path_data.joinpath('person.txt')
path_users = path_data.joinpath('users.txt')
path_ratings = path_data.joinpath('ratings.txt')


# path_sql_movies = Path().cwd().joinpath('postgres_legacy/init_db_movies.sql')
# with path_sql_movies.open('r') as f:
#     sql_init_movies = f.read()
#
# path_sql_users = Path().cwd().joinpath('postgres_legacy/init_db_users.sql')
# with path_sql_users.open('r') as f:
#     sql_init_users = f.read()
#
# path_sql_ugc = Path().cwd().joinpath('postgres_legacy/init_db_ugc.sql')
# with path_sql_ugc.open('r') as f:
#     sql_init_ugc = f.read()


def init_movies():
    conn = psycopg2.connect(f"""
        host={POSTGRES_HOST}
        port={POSTGRES_PORT}
        dbname={POSTGRES_MOVIES_DB}
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode={SSL_MODE}
    """)

    with conn.cursor() as cur:
        # cur.execute(sql_init_movies)

        with path_film_work.open('r') as f:
            cur.copy_from(f, 'content.film_work')
        with path_person_film_work.open('r') as f:
            cur.copy_from(f, 'content.person_film_work')
        with path_person.open('r') as f:
            cur.copy_from(f, 'content.person')
        with path_genre_film_work.open('r') as f:
            cur.copy_from(f, 'content.genre_film_work')
        with path_genre.open('r') as f:
            cur.copy_from(f, 'content.genre')

    conn.commit()
    conn.close()

    print('Таблицы с данными успещно созданы для бд movies', flush=True)


def init_users():
    conn = psycopg2.connect(f"""
        host={POSTGRES_HOST}
        port={POSTGRES_PORT}
        dbname={POSTGRES_USERS_DB}
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode={SSL_MODE}
    """)

    with conn.cursor() as cur:
        # cur.execute(sql_init_users)

        with path_users.open('r') as f:
            cur.copy_from(f, f'{POSTGRES_USERS_DB}.users')

    conn.commit()
    conn.close()

    print('Таблица users успещно создана для бд users', flush=True)


def init_ugc():
    conn = psycopg2.connect(f"""
        host={POSTGRES_HOST}
        port={POSTGRES_PORT}
        dbname={POSTGRES_UGC_DB}
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode={SSL_MODE}
    """)

    with conn.cursor() as cur:
        # cur.execute(sql_init_ugc)

        with path_ratings.open('r') as f:
            cur.copy_from(f, 'user_content.ratings')

    conn.commit()
    conn.close()

    print('Таблица ratings успещно создана для бд ugc', flush=True)


if __name__ == '__main__':
    init_movies()
    init_users()
    init_ugc()
