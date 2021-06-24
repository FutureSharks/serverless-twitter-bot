# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger()


def run(api: object, options: dict, recipient: str, state: dict):
    recent_tweet = api.get_most_recent_tweet(recipient)

    if recent_tweet == None:
        logger.info(f"No tweets for {recipient}")
        return

    if recent_tweet.retweeted:
        logger.info(f"Tweet ID {recent_tweet.id} from {recent_tweet.user.screen_name} already retweeted")
        return

    result = api.retweet_tweet(recent_tweet.id)

    if result.retweeted:
        logger.info(f"Retweeted tweet ID {recent_tweet.id} from {recent_tweet.user.screen_name}")
    else:
        logger.error(f"Retweet failed for tweet ID {recent_tweet.id} from {recent_tweet.user.screen_name}")

    return state
