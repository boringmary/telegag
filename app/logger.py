import logging
from typing import Type
from functools import wraps

default_handler = logging.StreamHandler()
default_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
)


def create_logger(name, debug_level: str) -> logging.Logger:
    '''Create app logger.
    :param: name: name of the app to be logged
    :param: debug_level: python standard level of debug(DEBUG, INFO...)
    '''
    logger = logging.getLogger(name)

    logger.setLevel(debug_level)
    logger.addHandler(default_handler)

    return logger


def applog(func):
    @wraps(func)
    def wrap(self, *args, **kwargs):
        self.log.info(f"Starting {func.__name__} with parameters: args - {args}, kwargs = {kwargs}")
        rse = func(self, *args, **kwargs)
        self.log.info(f"Finishing {func.__name__}")
        return rse
    return wrap
