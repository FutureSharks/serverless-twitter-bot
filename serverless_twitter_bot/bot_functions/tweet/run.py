# -*- coding: utf-8 -*-

import logging
from serverless_twitter_bot import select_new_random_item


logger = logging.getLogger()


def run(api: object, options: dict, state: dict):
    if "already_tweeted" not in state:
        state["already_tweeted"] = []

    index_to_tweet, already_tweeted = select_new_random_item(
        choices=options["config"]["tweets"],
        previously_chosen=state["already_tweeted"]
    )

    tweet_text = options["config"]["tweets"][index_to_tweet]

    result = api.send_tweet(tweet_text)

    if result.id:
        state["already_tweeted"] = already_tweeted
        logger.info(f"Sent tweet ID {result.id} with text '{tweet_text}'")
    else:
        logger.error(f"Failed to send tweet index {tweet_indexes}: {result}")

    return state
