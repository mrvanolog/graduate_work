import logging
from datetime import datetime
from pytz import timezone

from typing import List


def create_formatter():
    def timetz(*args):
        return datetime.now(tz).timetuple()

    tz = timezone('Europe/Moscow')

    logging.Formatter.converter = timetz

    return logging.Formatter(
        "[%(asctime)s]\t[%(name)s]\t[%(levelname)s]\t%(message)s", "%Y-%m-%d %H:%M:%S"
    )


def create_handler_console(format: logging.Formatter) -> logging.StreamHandler:
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(format)

    return console


def create_logger(logger_name: str, handler: List[logging.Handler]) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    for h in handler:
        logger.addHandler(h)
    logger.setLevel(logging.DEBUG)

    return logger


def set_up_logging():
    # define formatter
    default_format = create_formatter()

    # define handlers
    console = create_handler_console(default_format)

    # add handlers to loggers
    create_logger("main", [console])
    create_logger("backoff", [console])
