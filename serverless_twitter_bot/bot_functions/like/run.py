# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger()


def run(api: object, options: dict, recipient: str, state: dict):
    recent_tweet = api.get_most_recent_tweet(recipient)

    if recent_tweet == None:
        logger.info(f"No tweets for {recipient}")
        return

    if recent_tweet.favorited:
        logger.info(f"Tweet ID {recent_tweet.id} from {recent_tweet.user.screen_name} already liked")
        return

    result = api.like_tweet(recent_tweet.id)

    if result.favorited:
        logger.info(f"Liked tweet ID {recent_tweet.id} from {recent_tweet.user.screen_name}")
    else:
        logger.error(f"Like failed for tweet ID {recent_tweet.id} from {recent_tweet.user.screen_name}")

    return state
