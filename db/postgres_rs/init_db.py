import os
from pathlib import Path
import psycopg2

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', default='rc1b-9g35diheb1pr3mvu.mdb.yandexcloud.net')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', default='6432')
POSTGRES_USER = os.environ.get('POSTGRES_USER', default='user_admin')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', default='qwerty123')

path_sql_data = Path().cwd().joinpath('init_db_data.sql')
with path_sql_data.open('r') as f:
    sql_init_data = f.read()

path_sql_predictions = Path().cwd().joinpath('init_db_predictions.sql')
with path_sql_predictions.open('r') as f:
    sql_init_predictions = f.read()


def init_data():
    postgres_db = 'rs-data'

    conn = psycopg2.connect(f"""
        host={POSTGRES_HOST}
        port={POSTGRES_PORT}
        dbname={postgres_db}
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)

    with conn.cursor() as cur:
        cur.execute(sql_init_data)

    conn.commit()
    conn.close()

    print('Таблицы успешно созданы для бд rs-data', flush=True)


def init_predictions():
    postgres_db = 'rs-predictions'

    conn = psycopg2.connect(f"""
        host={POSTGRES_HOST}
        port={POSTGRES_PORT}
        dbname={postgres_db}
        user={POSTGRES_USER}
        password={POSTGRES_PASSWORD}
        target_session_attrs=read-write
        sslmode=verify-full
    """)

    with conn.cursor() as cur:
        cur.execute(sql_init_predictions)

    conn.commit()
    conn.close()

    print('Таблицы успешно созданы для бд rs-predictions', flush=True)


def main():
    init_data()
    init_predictions()


if __name__ == '__main__':
    main()
