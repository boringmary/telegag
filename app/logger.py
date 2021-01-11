import logging
from typing import Type

default_handler = logging.StreamHandler()
default_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
)


def create_logger(name, debug_level: str) -> Type[logging.Logger]:
    '''Create app logger.
    :param: name: name of the app to be logged
    :param: debug_level: python standard level of debug(DEBUG, INFO...)
    '''
    logger = logging.getLogger(name)

    logger.setLevel(debug_level)
    logger.addHandler(default_handler)

    return logger
