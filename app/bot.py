#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

import os
import praw
import yaml
import logging
from typing import Dict, Type, List
from pprint import pprint
from pathlib import Path


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
    catch_error,
    ChannelNotFoundError,
    IncorrectDareError,
    IncorrectInputError
)
from app.logger import create_logger

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

    caption: str = """
    *{likes}* likes, *{coms}* comments
    """
    # [original post]({url})
    # *{title}*

    def __init__(
        self,
        config_file: str = default_config_filename,
        credentials_file: str = default_credentials_filename,
        token: str = token
    ) -> None:
        self.cfg = self.get_config(config_file)
        self.logger = self.get_logger(self.cfg['LOG_LEVEL'])
        self.token = token
        self.init_clients()

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

    def init_clients(self) -> None:
        '''Init all bot's API clients
        Like reddit and (!TODO)9gag
        '''
        self.reddit = self.init_reddit_client()

    def init_reddit_client(self) -> Type[praw.Reddit]:
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

    def get_logger(self, log_level: str) -> Type[logging.Logger]:
        '''Get app logger (standard python logging.Logger)
        :param: log_level: config parameter of logging level (DEBUG, INFO...)
        '''
        return create_logger(self.app_name, log_level)

    def handle_exception(self):
        '''Handle exception happening in the bot
        '''
        pass

    def subscribe_on_reddit_channel(
        self,
        update: Type[Update],
        context: Type[CallbackContext],
        channel: Type[praw.models.Subreddit]
    ) -> None:
        '''
        '''
        chat_id = update.message.from_user.id
        try:
            due = int(context.args[1])
            if not due or due < 0:
                raise IncorrectDareError

            limit = int(context.args[2]) or 1

            context.job_queue.run_repeating(
                self.send_reddit_post,
                name=str(chat_id),
                context={'chat_id': chat_id, 'channel': channel, 'limit': limit},
                interval=due,
                first=10
            )

            text = 'Timer successfully set!'
            update.message.reply_text(text)

        except (IndexError, ValueError):
            raise
            update.message.reply_text('Please use command: /set <seconds>')

    def unsubscribe_from_job(
        self,
        update: Type[Update],
        context: Type[CallbackContext],
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

    def show_posts(
        self,
        update: Type[Update],
        context: Type[CallbackContext]
    ) -> None:
        '''
        '''
        channel = self.get_channel(context)
        chat_id = update.message.from_user.id
        limit = context.args[1]
        self.send_reddit_post(context, channel, chat_id, limit)

    def send_reddit_post(
        self,
        context: Type[CallbackContext],
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

    def _send_reddit_post(
        self,
        context: Type[CallbackContext],
        post: Type[praw.models.Submission],
        chat_id: int
    ) -> None:
        '''
        '''
        # pprint(x.__dict__)
        if getattr(post, "media"):
            video = post.media.get('reddit_video') or post.preview['reddit_video_preview']
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
        elif getattr(post, "preview"):
            context.bot.send_animation(
                chat_id=chat_id,
                animation=post.preview['reddit_video_preview']['fallback_url'],
                # caption=self.caption.format(
                #     title=x.title,
                #     likes=x.ups,
                #     coms=x.num_comments
                # ),
                # parse_mode=PARSEMODE_MARKDOWN_V2
            )
        else:
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

    # TODO: define generic type for all clients (like reddit, 9gag etc.s)
    # def get_channel_by_name(self, client: Type[self.praw.Reddit], name: str) -> Type[praw.reddit.Subreddit]:
    #     '''Get instanse of the channel by its name
    #     :param: client: client to search channel (reddit/9gag)
    #     :param: name: channel name
    #     '''
    #     if isinstance(self.client, self.praw.Reddit):
    #         channel = get_reddit_channel_by_name(name)
    #     return channel

    def get_reddit_channel_by_name(self, name: str) -> Type[praw.reddit.Subreddit]:
        '''Validate channel name provided by user
        :param: name: name of the channel
        '''
        channels = self.reddit.subreddits.search_by_name(name)
        if not channels:
            raise ChannelNotFoundError
        return channels[0]

    def get_channel(self, context: Type[CallbackContext]) -> List[Type[praw.reddit.Subreddit]]:
        raw_channel = context.args[0]
        if not raw_channel:
            raise IncorrectInputError
        return self.get_reddit_channel_by_name(raw_channel)

    @catch_error
    def subscribe_on_reddit(
        self,
        update: Type[Update],
        context: Type[CallbackContext]
    ) -> None:
        channel = get_channel(context)
        self.subscribe_on_reddit_channel(update, context, channel)

    @catch_error
    def menu_categories(
        self,
        update: Type[Update],
        context: Type[CallbackContext]
    ) -> None:
        items = [x.display_name for x in self.get_popular_subreddits()]
        update.message.reply_text(
            "Choose the channel you want to subscribe",
            reply_markup=self.get_main_menu_kb(items)
        )

    @catch_error
    def get_main_menu(
        self,
        update: Type[Update],
        context: Type[CallbackContext]
    ) -> None:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text="",
            reply_markup=get_main_menu_kb()
        )

    @catch_error
    def get_main_menu_kb(self, items: List[str]) -> Type[InlineKeyboardMarkup]:
        '''Show menu
        '''
        keyboard = [[InlineKeyboardButton(x, callback_data='m1')] for x in items]
        return InlineKeyboardMarkup(keyboard)

    def run(self):
        '''Run the application, register all bot handlers.
        '''
        updater = Updater(self.token, use_context=True)
        dispatcher = updater.dispatcher


        dispatcher.add_handler(CommandHandler("menu", self.menu_categories))
        dispatcher.add_handler(CommandHandler("sub", self.subscribe_on_reddit))
        dispatcher.add_handler(CommandHandler("show", self.show_posts))
        dispatcher.add_handler(CallbackQueryHandler(self.get_main_menu, pattern='main'))

        updater.start_polling()

        updater.idle()
