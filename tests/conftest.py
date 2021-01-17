#!/usr/bin/env python
import pytest
from app.bot import Bot


@pytest.fixture(scope='session')
def bot_info():
    return get_bot()


@pytest.fixture(scope='session')
def bot(bot_info):
    return make_bot(bot_info)


def make_bot(bot_info, **kwargs):
    return Bot(config_file="../tests/config.yaml")


def get_bot():
    return {
        'token': '1524512463:AAG61K5e5RfQtI5YSImztooX4T_xlWeSS2k',
        'channel_id': '@telegag_unit_test_bot',
        'bot_name': 'telegag_unit_test_bot',
        'bot_username': '@telegag_unit_test_bot',
    }
