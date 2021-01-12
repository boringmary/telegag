import yaml
from functools import wraps
from typing import Dict, Callable, Type

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from telegram import Update


class TelegramUserError(object):
    """docstring for FileNotFoundError"""
    def __init__(self, update, message):
        update.message.reply_text(
            message
        )


class ChannelNotFoundError(TelegramUserError):
    """docstring for FileNotFoundError"""
    def __init__(self, update):
        message = "Incorrect channel name"
        super().__init__(update, message)


class IncorrectDareError(TelegramUserError):
    """docstring for FileNotFoundError"""
    def __call__(self, update):
        message = "Incorrect date"
        super().__init__(update, message)


class IncorrectInputError(TelegramUserError):
    """docstring for FileNotFoundError"""
    def __init__(self, update):
        message = "Incorrect usage of the command. Please see /help"
        super().__init__(update, message)


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
