import os
from pathlib import Path
import psycopg2

POSTGREWS_HOST = os.environ.get('POSTGREWS_HOST',
                                default='rc1a-80npisto5z5x0n4n.mdb.yandexcloud.net')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', default='6432')
POSTGRES_USER = os.environ.get('POSTGRES_USER', default='user_admin')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', default='qwerty123')

path_data = Path().cwd().joinpath('data')
path_film_work = path_data.joinpath('film_work.txt')
path_genre_film_work = path_data.joinpath('genre_film_work.txt')
path_genre = path_data.joinpath('genre.txt')
path_person_film_work = path_data.joinpath('person_film_work.txt')
path_person = path_data.joinpath('person.txt')

path_sql_movies = Path().cwd().joinpath('init_movies.sql')
with path_sql_movies.open('r') as f:
    sql_init_movies = f.read()

path_sql_users = Path().cwd().joinpath('init_users.sql')
with path_sql_users.open('r') as f:
    sql_init_users = f.read()


def init_movies():
    postgres_db = 'movies'

    conn = psycopg2.connect(f"""
        host={POSTGREWS_HOST}
        port={POSTGRES_PORT}
        dbname={postgres_db}
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)

    with conn.cursor() as cur:
        cur.execute(sql_init_movies)

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
    postgres_db = 'users'

    conn = psycopg2.connect(f"""
        host={POSTGREWS_HOST}
        port={POSTGRES_PORT}
        dbname={postgres_db}
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)

    with conn.cursor() as cur:
        cur.execute(sql_init_users)

    conn.commit()
    conn.close

    print('Таблица users успещно создана для бд users', flush=True)


def main():
    init_movies()
    init_users()


if __name__ == '__main__':
    main()
