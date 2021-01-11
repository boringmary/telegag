import yaml
from functools import wraps
from typing import Dict, Callable, Type

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from telegram import Update


class ChannelNotFoundError(Exception):
    """docstring for FileNotFoundError"""
    def __init__(self):
        super().__init__("Channel with this name hasn't been found, please try another one.")


class IncorrectDareError(Exception):
    """docstring for FileNotFoundError"""
    def __init__(self):
        super().__init__("Please set a correct date.")


class IncorrectInputError(Exception):
    """docstring for FileNotFoundError"""
    def __init__(self):
        super().__init__("Please set a correct channel and date.")


def load_yaml(filepath: str) -> Dict:
    '''Load yaml file and return python dictionary.
    :param: filepath: full path of the file
    '''
    try:
        with open(filepath, 'r') as stream:
            return yaml.load(stream, Loader=Loader)
    except FileNotFoundError as exc:
        # TODO implement yaml error handling
        raise
    except yaml.YAMLError as exc:
        # TODO implement yaml error handling
        raise


def catch_error(f):
    @wraps(f)
    def wrap(self, bot, update: Type[Update]) -> Callable:
        try:
            return f(self, bot, update)
        except ChannelNotFoundError as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text=e.message)
    return wrap
