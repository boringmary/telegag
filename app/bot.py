#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

import os
import praw
import yaml
import logging
from pprint import pprint
from pathlib import Path
from typing import Dict, List, Tuple


from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    Updater
)
from telegram.constants import PARSEMODE_MARKDOWN_V2
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from app.helpers import (
    load_yaml,
    ChannelNotFoundError,
    IncorrectDareError,
    IncorrectInputError
)
from app.logger import create_logger, applog

TYPE_CHECKING = True

if TYPE_CHECKING:
    from telegram.ext import CallbackContext, Dispatcher


class Bot(object):
    """Bot implements a telegram bot application
    :param: config_file: filename of the config file
    :param: credentials: fileanme of the aws credentials
    """

    default_config_filename: str = "config.yaml"
    default_credentials_filename: str = "credentials"
    app_name: str = 'telegag_bot'

    token: str = "1426129428:AAHzbIpophVpFNUWPSziKc4u1SjikYW6qzE"

    caption: str = '''
    *{likes}* likes, *{coms}* comments
    '''
    # [original post]({url})
    # *{title}*

    help_command_md: str = "/*_{command}_* \- {description}"

    commands_md: Tuple = (
        ("help", "show help"),
        ("show", "show latest n posts for a channel\. Usage: `show aww 3` will show 3 latest @aww posts"),
        ("menu", "show available categories"),
        ("sub", "subscribe to the channel\. Usage: `sub aww 30 1` will subscribe you to @aww, showing 1 post every 30 seconds")
    )

    def __init__(
        self,
        config_file: str = default_config_filename,
        credentials_file: str = default_credentials_filename,
        token: str = token
    ) -> None:

        self.cfg = self.get_config(config_file)
        self.log = self.get_logger(self.cfg['LOG_LEVEL'])
        self.token = token
        self.init_clients()

    @property
    def name(self):
        '''Returns name of the bot
        '''
        return cls.app_name

    @property
    def help_md(self):
        '''Returns help message
        '''
        return "\n".join([self.help_command_md.format(
            command=x[0],
            description=x[1]
        ) for x in self.commands_md])

    def get_config(self, filename: str) -> Dict:
        '''Load app configuration from provided filename
        :param: filename: filename of the config file
        '''
        filename = (Path(__file__).parent).joinpath(filename)
        try:
            return load_yaml(filename)
        except OSError as e:
            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise

    def get_logger(self, log_level: str) -> logging.Logger:
        '''Get app logger (standard python logging.Logger)
        :param: log_level: config parameter of logging level (DEBUG, INFO...)
        '''
        return create_logger(self.app_name, log_level)

    @applog
    def init_clients(self) -> None:
        '''Init all bot's API clients
        Like reddit and (!TODO)9gag
        '''
        self.reddit = self.init_reddit_client()

    @applog
    def init_reddit_client(self) -> praw.Reddit:
        '''Init reddit client with credentials provided by
        config_file. client_secret is remains blank because of
        the back capability of reddit API.
        '''
        return praw.Reddit(
            client_id=self.cfg['REDDIT_CLIENT_ID'],
            client_secret="",
            password=self.cfg['REDDIT_USERNAME'],
            user_agent="USERAGENT",
            username=self.cfg['REDDIT_PASSWORD']
        )

    @applog
    def subscribe_on_reddit_channel(
        self,
        update: Update,
        context: CallbackContext,
        channel: praw.models.Subreddit
    ) -> None:
        '''
        '''
        chat_id = update.message.from_user.id
        try:
            due = int(context.args[1])
            if not due or due < 0:
                self.log.debug(f"Incorrect date set: {due}")
                raise IncorrectDareError

            limit = int(context.args[2]) or 1

            job = self.send_reddit_post

            self.log.info(f"Registering job {job} for chat_id {chat_id}, interval {interval}, limit {limit}")
            context.job_queue.run_repeating(
                job,
                name=str(chat_id),
                context={'chat_id': chat_id, 'channel': channel, 'limit': limit},
                interval=due,
                first=10
            )
            self.log.info("Job registered")

            update.message.reply_text('Timer successfully set!')

        except (IndexError, ValueError) as e:
            self.log.error(f"An error occured {e.message}")
            update.message.reply_text('Please use command: /set <seconds>')

    @applog
    def unsubscribe_from_job(
        self,
        update: Update,
        context: CallbackContext,
    ) -> None:
        '''
        '''
        chat_id = update.message.from_user.id
        job_removed = remove_jobs_if_exists(str(chat_id), context)
        text = 'You are successfully unsubscribed!' if job_removed else 'You have no active subscriptions.'
        update.message.reply_text(text)

    def get_popular_subreddits(self) -> List[praw.models.Subreddit]:
        '''Get list of popular subreddits
        '''
        return list(self.reddit.subreddits.popular())

    @applog
    def show_posts(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        '''
        '''
        channel = self.get_channel(context)
        chat_id = update.message.from_user.id
        limit = context.args[1]
        self.send_reddit_post(context, channel, chat_id, limit)

    @applog
    def send_reddit_post(
        self,
        context: CallbackContext,
        channel: str = None,
        chat_id: int = None,
        limit: int = None
    ) -> None:
        '''
        '''
        channel = channel or context.job.context['channel']
        chat_id = chat_id or context.job.context['chat_id']
        limit = limit or context.job.context['limit']
        s = list(channel.top(time_filter="day", limit=int(limit)))
        for post in s:
            self._send_reddit_post(context, post, chat_id)

    @applog
    def _send_reddit_post(
        self,
        context: CallbackContext,
        post: praw.models.Submission,
        chat_id: int
    ) -> None:
        '''
        '''
        self.log.debug(f"Sending post {post.id} to chat_id {chat_id}")

        if getattr(post, "media"):
            video = post.media.get('reddit_video') or post.preview['reddit_video_preview']

            self.log.debug(f"Starting video {video['fallback_url']} stream")
            context.bot.send_video(
                chat_id=chat_id,
                video=video['fallback_url'],
                caption=self.caption.format(
                    title=post.title,
                    likes=post.ups,
                    coms=post.num_comments
                ),
                parse_mode=PARSEMODE_MARKDOWN_V2
            )
            self.log.debug("Video sent")

        elif getattr(post, "preview"):
            anim_url = post.preview['reddit_video_preview']['fallback_url']
            self.log.debug(f"Starting animation {anim_url} stream")

            context.bot.send_animation(
                chat_id=chat_id,
                animation=anim_url,
                caption=self.caption.format(
                    title=x.title,
                    likes=x.ups,
                    coms=x.num_comments
                ),
                parse_mode=PARSEMODE_MARKDOWN_V2
            )
            self.log.debug("Animation sent")

        else:
            self.log.debug(f"Starting photo {post.url} stream")

            context.bot.send_photo(
                chat_id=chat_id,
                photo=post.url,
                caption=self.caption.format(
                    title=post.title,
                    likes=post.ups,
                    coms=post.num_comments
                ),
                parse_mode=PARSEMODE_MARKDOWN_V2
            )

            self.log.debug("Photo sent")

    # TODO: define generic type for all clients (like reddit, 9gag etc.s)
    # def get_channel_by_name(self, client: Type[self.praw.Reddit], name: str) -> Type[praw.reddit.Subreddit]:
    #     '''Get instanse of the channel by its name
    #     :param: client: client to search channel (reddit/9gag)
    #     :param: name: channel name
    #     '''
    #     if isinstance(self.client, self.praw.Reddit):
    #         channel = get_reddit_channel_by_name(name)
    #     return channel

    @applog
    def get_reddit_channel_by_name(self, name: str) -> praw.reddit.Subreddit:
        '''Validate channel name provided by user
        :param: name: name of the channel
        '''
        channels = self.reddit.subreddits.search_by_name(name)
        if not channels:
            ChannelNotFoundError()
        return channels[0]

    @applog
    def get_channel(self, context: CallbackContext) -> List[praw.reddit.Subreddit]:
        raw_channel = context.args[0]
        if not raw_channel:
            raise IncorrectInputError
        return self.get_reddit_channel_by_name(raw_channel)

    @applog
    def show_help(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        text = self.help_md
        update.message.reply_text(
            text,
            parse_mode=PARSEMODE_MARKDOWN_V2
        )

    @applog
    def subscribe_on_reddit(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        '''
        '''
        if not context.args:
            IncorrectInputError(context, update)
            return
        channel = self.get_channel(context)
        self.subscribe_on_reddit_channel(update, context, channel)

    @applog
    def menu_categories(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        items = [x.display_name for x in self.get_popular_subreddits()]
        update.message.reply_text(
            "Choose the channel you want to subscribe",
            reply_markup=self.get_main_menu_kb(items)
        )

    @applog
    def get_main_menu(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text="",
            reply_markup=get_main_menu_kb()
        )

    @applog
    def get_main_menu_kb(self, items: List[str]) -> InlineKeyboardMarkup:
        '''Show menu
        '''
        keyboard = [[InlineKeyboardButton(x, callback_data='m1')] for x in items]
        return InlineKeyboardMarkup(keyboard)

    def run(self):
        '''Run the application, register all bot handlers.
        '''
        self.log.info("Starting updater")
        updater = Updater(self.token, use_context=True)

        self.log.info("Starting dispatcher")
        dispatcher = updater.dispatcher

        self.log.info("Registering handlers")
        dispatcher.add_handler(CommandHandler("menu", self.menu_categories))
        dispatcher.add_handler(CommandHandler("help", self.show_help))
        dispatcher.add_handler(CommandHandler("sub", self.subscribe_on_reddit))
        dispatcher.add_handler(CommandHandler("show", self.show_posts))
        dispatcher.add_handler(CallbackQueryHandler(self.get_main_menu, pattern='main'))

        self.log.info("Starting polling")
        updater.start_polling()

        updater.idle()
