# -*- coding: utf-8 -*-

import logging
import datetime
from serverless_twitter_bot import list_files, load_image_file, select_new_random_item
from tweepy import Cursor


# disable PIL debug logs
pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)


logger = logging.getLogger()


def run(api: object, options: dict, state: dict, recipient: str):
    recent_tweet = api.get_most_recent_tweet(recipient)

    if not recent_tweet:
        logger.info(f"No recent tweet for user {recipient}")
        return state

    recent_tweet_age = datetime.datetime.utcnow() - recent_tweet.created_at
    if recent_tweet_age.seconds > 10800:
        logger.info(f"Recent tweet too old for tweet ID {recent_tweet.id}, user {recipient}")
        return state

    replies = Cursor(api.api.search, q='to:{} filter:replies conversation_id:{}'.format(recipient, recent_tweet.id), tweet_mode='extended').items()

    for i in range(options["config"].get("reply_count", 20)):
        try:
            reply = replies.next()
        except StopIteration:
            break

        if reply.user.default_profile_image:
            logger.debug(f"Default profile image for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        age = datetime.datetime.utcnow() - reply.created_at
        if age.seconds > 10800:
            logger.debug(f"Tweet too old for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        if reply.user.followers_count < 30:
            logger.debug(f"Followers count too low for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        if reply.user.friends_count < 30:
            logger.debug(f"Friend count too low for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        if reply.user.statuses_count < 50:
            logger.debug(f"Status count too low for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        if reply.user.following:
            logger.debug(f"Already following user {reply.user.screen_name}")
            continue

        logger.debug(f"Following user {reply.user.screen_name}")
        result = reply.user.follow()

        if options["config"].get("like_tweets"):
            like_result = api.like_tweet(reply.id)
            logger.info(f"Liked tweet ID {reply.id}, from {reply.user.screen_name}")

    return state
