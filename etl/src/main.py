import logging
import time
from datetime import datetime
from typing import Dict, List

import psycopg2.extras

from conf.log import set_up_logging
from conf import settings
from conf.utils import backoff

set_up_logging()
logger = logging.getLogger("main")

DATE_FILTER: datetime = datetime(2021, 6, 11, 17, 17)


@backoff('ugc')
def connect_ugc() -> psycopg2._connect:
    return psycopg2.connect(f"""
        host={settings.POSTGRES_UGC_HOST}
        port={settings.POSTGRES_UGC_PORT}
        dbname={settings.POSTGRES_UGC_DB}
        user={settings.POSTGRES_UGC_USER}
        password={settings.POSTGRES_UGC_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)


@backoff('movies')
def connect_movies() -> psycopg2._connect:
    return psycopg2.connect(f"""
        host={settings.POSTGRES_MOVIES_HOST}
        port={settings.POSTGRES_MOVIES_PORT}
        dbname={settings.POSTGRES_MOVIES_DB}
        user={settings.POSTGRES_MOVIES_USER}
        password={settings.POSTGRES_MOVIES_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)


@backoff('rs-data')
def connect_rs_data() -> psycopg2._connect:
    return psycopg2.connect(f"""
        host={settings.POSTGRES_DATA_HOST}
        port={settings.POSTGRES_DATA_PORT}
        dbname={settings.POSTGRES_DATA_DB}
        user={settings.POSTGRES_DATA_USER}
        password={settings.POSTGRES_DATA_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)


def get_date_filter() -> datetime:
    global DATE_FILTER

    date_filter = DATE_FILTER
    DATE_FILTER = datetime.now()

    return date_filter


def extract(conn_ugc: psycopg2._connect, conn_movies: psycopg2._connect) -> Dict[str, List[tuple]]:
    result = {}

    date_filter = get_date_filter()
    with conn_ugc.cursor() as cur:
        cur.execute(f"""
            SELECT DISTINCT {settings.columns_ratings}
            FROM user_content.ratings
            WHERE created_at >= '{date_filter}'
        """)
        result['ratings'] = cur.fetchall()

    with conn_movies.cursor() as cur:
        cur.execute(f"""
            SELECT DISTINCT {settings.columns_movies}
            FROM content.film_work
            WHERE updated_at >= '{date_filter}'
        """)
        result['movies'] = cur.fetchall()

    return result


def transform(data: Dict[str, List[tuple]]) -> Dict[str, List[tuple]]:
    ratings = []
    ratings_prep = data['ratings']
    for rating in ratings_prep:
        row = (rating[0], rating[1], rating[2], str(rating[3]))
        ratings.append(row)

    movies = []
    movies_prep = data['movies']
    for movie in movies_prep:
        row = (movie[0], movie[1], movie[6], movie[7], str(movie[8]), str(movie[9]))
        movies.append(row)

    return {'ratings': ratings, 'movies': movies}


def load(conn_rs_data: psycopg2._connect, values: Dict[str, List[tuple]]) -> bool:
    with conn_rs_data.cursor() as cur:
        psycopg2.extras.execute_values(cur, settings.sql_insert_ratings, values['ratings'])
        psycopg2.extras.execute_values(cur, settings.sql_insert_movies, values['movies'])

    conn_rs_data.commit()


def main():
    conn_ugc = connect_ugc()
    conn_movies = connect_movies()
    conn_rs_data = connect_rs_data()
    time_start = time.time()

    while True:
        try:
            time_now = time.time()
            if time_now - time_start <= settings.FLUSH_SECONDS:
                continue

            logger.info('Начата выгрузка данных...')

            raw_data = extract(conn_ugc, conn_movies)
            values = transform(raw_data)
            load(conn_rs_data, values)

            logger.info(f'- время загрузки: {time.time() - time_now} с')

            time_start = time_now

        except psycopg2.DatabaseError as e:
            logger.error(f'Ошибка в соединении с Postgres: {e}')
            conn_ugc = connect_ugc()
            conn_movies = connect_movies()
            conn_rs_data = connect_rs_data()


if __name__ == '__main__':
    main()
