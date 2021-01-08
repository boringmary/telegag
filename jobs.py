# from telegram.constants import PARSEMODE_MARKDOWN_V2


# CAPTION = """
#     *{likes}* likes, *{coms}* comments
#     """
#     # [original post]({url})
#     # *{title}*


# def send_reddit_post(context, client):
#     s = list(client.subreddit("aww").top(time_filter="day", limit=1))
#     for x in s:
#         if getattr(x, "media"):
#             video = x.media.get('reddit_video') or x.preview['reddit_video_preview']
#             context.bot.send_video(
#                 chat_id=context.job.context,
#                 video=video['fallback_url'],
#                 caption=CAPTION.format(title=x.title, likes=x.ups, coms=x.num_comments),
#                 parse_mode=PARSEMODE_MARKDOWN_V2
#             )
#         else:
#             context.bot.send_photo(
#                 chat_id=context.job.context,
#                 photo=x.url,
#                 caption=CAPTION.format(title=x.title, likes=x.ups, coms=x.num_comments),
#                 parse_mode=PARSEMODE_MARKDOWN_V2
#             )


# registry = {
#     "send_reddit_post": send_reddit_post
# }
