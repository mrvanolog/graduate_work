import logging
import time
from functools import wraps

logger = logging.getLogger("backoff")


def backoff(db_name: str):
    def wrapper(func):

        @wraps(func)
        def inner(*args, **kwargs):
            t = 0.1
            border_sleep_time = 10

            while True:
                logger.info(f'Попытка подключения к {db_name}...')
                if t < border_sleep_time:
                    t *= 2

                try:
                    conn = func(*args, **kwargs)
                    logger.info(f'{db_name} успешно подключена')
                    return conn
                except Exception as e:
                    logger.error(f'Ошибка подключения: {e}')
                    logger.info(f'Повторная попытка через {t} секунд')
                    time.sleep(t)

        return inner

    return wrapper
