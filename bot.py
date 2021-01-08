#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

import os
import praw
import yaml
from pathlib import Path


from telegram.ext import Updater
from telegram.constants import PARSEMODE_MARKDOWN_V2
from telegram.ext import CommandHandler, MessageHandler, Filters

from helpers import load_yaml
from logger import create_logger


class Bot(object):
    """Bot implements a telegram bot application
    :param: config_file: filename of the config file
    :param: credentials: fileanme of the aws credentials
    """

    default_config_filename = "config.yaml"
    default_credentials_filename = "credentials"
    app_name = 'telegag_bot'

    caption = """
    *{likes}* likes, *{coms}* comments
    """
    # [original post]({url})
    # *{title}*

    def __init__(
        self,
        config_file=default_config_filename,
        credentials_file=default_credentials_filename
    ):
        self.cfg = self.get_config(config_file)
        self.logger = self.get_logger(self.cfg['LOG_LEVEL'])
        self.init_clients()

    def get_config(self, filename):
        '''Load app configuration from provided filename
        :param: filename: filename of the config file
        '''
        filename = (Path(__file__).parent).joinpath(filename)

        try:
            return load_yaml(filename)
        except OSError as e:
            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise

    def init_clients(self):
        '''Init all bot's API clients
        Like reddit and (!TODO)9gag
        '''
        self.init_reddit_client()

    def init_reddit_client(self):
        '''Init reddit client with credentials provided by
        config_file. client_secret is remains blank because of
        the back capability of reddit API.
        '''
        self.reddit = praw.Reddit(
            client_id=self.cfg['REDDIT_CLIENT_ID'],
            client_secret="",
            password=self.cfg['REDDIT_USERNAME'],
            user_agent="USERAGENT",
            username=self.cfg['REDDIT_PASSWORD']
        )

    def get_logger(self, log_level):
        '''Get app logger (standard python logging.Logger)
        :param: log_level: config parameter of logging level (DEBUG, INFO...)
        '''
        return create_logger(self.app_name, log_level)

    def handle_exception(self):
        '''Handle exception happening in the bot
        '''
        pass

    def remove_jobs_if_exists(name, context):
        '''
        '''
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_jobs:
            return False
        for job in current_jobs:
            job.schedule_removal()
        return True

    def subscribe_on_job(self, update, context):
        '''
        '''
        chat_id = update.message.from_user.id
        try:
            due = int(context.args[0])
            if due < 0:
                update.message.reply_text('Please set correct date')
                return

            context.job_queue.run_repeating(
                self.send_reddit_post,
                name=str(chat_id),
                context=chat_id,
                interval=due,
                first=10
            )

            text = 'Timer successfully set!'
            update.message.reply_text(text)

        except (IndexError, ValueError):
            raise
            update.message.reply_text('Please use command: /set <seconds>')

    def unsubscribe_from_job(self, update, context):
        chat_id = update.message.from_user.id
        job_removed = remove_jobs_if_exists(str(chat_id), context)
        text = 'You are successfully unsubscribed!' if job_removed else 'You have no active subscriptions.'
        update.message.reply_text(text)

        def __repr__(self):
            return f"<{type(self).__name__} {self.name!r}>"

    def send_reddit_post(self, context):
        '''
        '''
        s = list(self.reddit.subreddit("aww").top(time_filter="day", limit=1))
        for x in s:
            if getattr(x, "media"):
                video = x.media.get('reddit_video') or
                x.preview['reddit_video_preview']

                context.bot.send_video(
                    chat_id=context.job.context,
                    video=video['fallback_url'],
                    caption=self.caption.format(
                        title=x.title,
                        likes=x.ups,
                        coms=x.num_comments
                    ),
                    parse_mode=PARSEMODE_MARKDOWN_V2
                )
            else:
                context.bot.send_photo(
                    chat_id=context.job.context,
                    photo=x.url,
                    caption=self.caption.format(
                        title=x.title,
                        likes=x.ups,
                        coms=x.num_comments
                    ),
                    parse_mode=PARSEMODE_MARKDOWN_V2
                )

    def run(self):
        '''Run the application, register all bot handlers.
        '''
        updater = Updater(self.cfg['TOKEN'], use_context=True)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("set", self.subscribe_on_job))
        dispatcher.add_handler(CommandHandler("unset", self.unsubscribe_from_job))

        updater.start_polling()

        updater.idle()


if __name__ == '__main__':
    Bot().run()
