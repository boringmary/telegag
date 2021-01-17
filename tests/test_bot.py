import logging
import pytest
from app.logger import create_logger

# Dummy config (tests/config.yaml)
CFG_MOCK = {
    'LOG_LEVEL': 'DEBUG',
    'TOKEN': "dummy",
    'REDDIT_CLIENT_ID': "dummy",
    'REDDIT_USERNAME': "dummy",
    'REDDIT_PASSWORD': "dummy",
}

HELP_MSG = '''/*_help_* \- To show help use /help
/*_show_* \- To show latest n posts for a channel use `/show aww 3`, it will show 3 latest @aww posts
/*_sub_* \- To subscribe to the channel use `/sub aww 30 1`, it will subscribe you to @aww, showing 1 post every 30 seconds'''


@pytest.mark.parametrize("input,expected", [
    ("INFO", logging.INFO),
    ("DEBUG", logging.DEBUG),
])
def test_logger(input, expected):
    logger = create_logger("name", input)
    assert isinstance(logger, logging.Logger)
    assert logger.level == expected
    assert logger.name == "name"


def test_logger_fail():
    with pytest.raises(ValueError):
        create_logger("name", "DUMMY")


@pytest.mark.parametrize("input,expected", [
    ("INFO", logging.INFO),
    ("DEBUG", logging.DEBUG),
])
def test_get_logger(input, expected, bot):
    logger = bot.get_logger(input)
    assert isinstance(logger, logging.Logger)
    assert logger.level == expected
    assert logger.name == bot.app_name


def test_get_logger_fail(bot):
    with pytest.raises(ValueError):
        bot.get_logger("DUMMY")


def test_config(bot):
    assert bot.cfg == CFG_MOCK


def test_get_config(bot):
    assert bot.get_config("../tests/config.yaml") == CFG_MOCK


def test_get_config_fails(bot):
    with pytest.raises(OSError):
        bot.get_config("../dummy.yaml")


def test_reddit_client(bot):
    assert bot.reddit


# TODO: probably need to cover reddit api errors
def test_init_reddit_client(bot, monkeypatch):
    def mock(**kwargs):
        return res
    res = {"created": True}
    monkeypatch.setattr("praw.Reddit", mock)
    assert bot.init_reddit_client() == res


def test_get_help_messagee(bot):
    assert bot.help_md == HELP_MSG
