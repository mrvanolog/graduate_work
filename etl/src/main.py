import datetime as dt
import logging.config
import os
import time
from pathlib import Path

import psycopg2
import yaml
from urllib3.exceptions import HTTPError as BaseHTTPError
from utils.etl import ETL
from utils.state import BaseStorage, JsonFileStorage

UPDATE_INTERVAL = dt.timedelta(seconds=20)

# initialising logging
path_log_conf = Path(__file__).parent.joinpath("log_conf.yaml")
with path_log_conf.open("r") as f:
    data = f.read()
    log_conf = yaml.safe_load(data)

logging.config.dictConfig(log_conf)
logger = logging.getLogger("main")

# setting global constants
DSL = {'dbname': os.getenv("POSTGRES_DB"),
       'user': os.getenv("POSTGRES_USER"),
       'host': os.getenv("POSTGRES_HOST"),
       'port': os.getenv("POSTGRES_PORT"),
       'password': os.getenv("POSTGRES_PASSWORD")}

ES_URL = os.getenv("ES_URL")
STATE_PATH = Path(__file__).parent.joinpath("state.json")


def set_up_connections(dsl: dict, es_url: str, storage: BaseStorage) -> ETL:
    """Set up connection to postgres, ES and create ETL object.
    """
    pg_conn = psycopg2.connect(**dsl)
    etl = ETL(pg_conn, es_url, storage)

    return etl


def reconnect(dsl: dict, es_url: str, storage: BaseStorage) -> ETL:
    """Try to reconnect to database.
    """
    start_sleep_time = 0.1
    n = 2
    border_sleep_time = 10

    logger.info("Trying to reconnect...")
    while True:
        t = start_sleep_time * 2 ** n
        if t > border_sleep_time:
            t = border_sleep_time

        try:
            etl = set_up_connections(dsl, es_url, storage)
            logger.info("Successfully reconnected.")
            return etl
        except Exception:
            time.sleep(t)


def main():
    while True:
        current_time = dt.datetime.utcnow() - UPDATE_INTERVAL

        if os.getenv("ETL_FIRST_RUN") == "True":
            time.sleep(UPDATE_INTERVAL.seconds)
            current_time = dt.datetime(1970, 1, 1, 1, 1, 1)
            os.environ["ETL_FIRST_RUN"] = "False"
        storage = JsonFileStorage(STATE_PATH)

        etl = set_up_connections(DSL, ES_URL, storage)

        while True:
            try:
                etl.etl_movies_film_work_updated(current_time)
                break
            except (psycopg2.DatabaseError, BaseHTTPError) as e:
                logger.error(f"Error in connection to db: {e}")
                etl = reconnect(DSL, ES_URL, storage)

        while True:
            try:
                etl.etl_movies_person_updated(current_time)
                break
            except (psycopg2.DatabaseError, BaseHTTPError) as e:
                logger.error(f"Error in connection to db: {e}")
                etl = reconnect(DSL, ES_URL, storage)

        while True:
            try:
                etl.etl_movies_genre_updated(current_time)
                break
            except (psycopg2.DatabaseError, BaseHTTPError) as e:
                logger.error(f"Error in connection to db: {e}")
                etl = reconnect(DSL, ES_URL, storage)

        while True:
            try:
                etl.etl_genre(current_time)
                break
            except (psycopg2.DatabaseError, BaseHTTPError) as e:
                logger.error(f"Error in connection to db: {e}")
                etl = reconnect(DSL, ES_URL, storage)

        while True:
            try:
                etl.etl_person(current_time)
                break
            except (psycopg2.DatabaseError, BaseHTTPError) as e:
                logger.error(f"Error in connection to db: {e}")
                etl = reconnect(DSL, ES_URL, storage)

        logger.info('Sleeping for {} sec ...'.format(UPDATE_INTERVAL.seconds))
        time.sleep(UPDATE_INTERVAL.seconds)


if __name__ == "__main__":
    main()
