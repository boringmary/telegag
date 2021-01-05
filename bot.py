#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

import praw
import yaml

from telegram.ext import Updater
from telegram.constants import PARSEMODE_MARKDOWN_V2
from telegram.ext import CommandHandler, MessageHandler, Filters

with open('config.yml', 'r') as stream:
    CF = yaml.load(stream)

reddit = praw.Reddit(
    client_id=CF['REDDIT_CLIENT_ID'],
    client_secret="",
    password=CF['REDDIT_USERNAME'],
    user_agent="USERAGENT",
    username=CF['REDDIT_PASSWORD']
)

CAPTION = """

*{likes}* likes, *{coms}* comments
"""
# [original post]({url})
# *{title}*

def callback_minute(context):

    s = list(reddit.subreddit("aww").top(time_filter="day", limit=1))
    for x in s:
        print(CAPTION.format(title=x.title, likes=x.ups, coms=x.num_comments))
        if getattr(x, "media"):
            video = x.media.get('reddit_video') or x.preview['reddit_video_preview']
            context.bot.send_video(
                chat_id=context.job.context,
                video=video['fallback_url'],
                caption=CAPTION.format(title=x.title, likes=x.ups, coms=x.num_comments),
                parse_mode=PARSEMODE_MARKDOWN_V2
            )
        else:
            context.bot.send_photo(
                chat_id=context.job.context,
                photo=x.url,
                caption=CAPTION.format(title=x.title, likes=x.ups, coms=x.num_comments),
                parse_mode=PARSEMODE_MARKDOWN_V2
            )


def remove_jobs_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def subscribe(update, context):
    chat_id = update.message.from_user.id
    try:
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Please set correct date')
            return

        context.job_queue.run_repeating(callback_minute, name=str(chat_id), context=chat_id, interval=due, first=10)

        text = 'Timer successfully set!'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Please use command: /set <seconds>')


def unsubscribe(update, context):
    chat_id = update.message.from_user.id
    job_removed = remove_jobs_if_exists(str(chat_id), context)
    text = 'You are successfully unsubscribed!' if job_removed else 'You have no active subscriptions.'
    update.message.reply_text(text)


def main():
    updater = Updater(CF['TOKEN'], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("set", subscribe))
    dispatcher.add_handler(CommandHandler("unset", unsubscribe))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
