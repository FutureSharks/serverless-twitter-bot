# -*- coding: utf-8 -*-

import logging
from serverless_twitter_bot import select_new_random_item


logger = logging.getLogger()


def run(api: object, options: dict, state: dict):
    # select a quote at random
    if "tweeted_quote" not in state:
        state["tweeted_quote"] = []

    quote_index_to_tweet, updated_tweeted_quotes = select_new_random_item(
        choices=options["config"]["quotes"],
        previously_chosen=state["tweeted_quote"]
    )

    # select author at random
    if "tweeted_author" not in state:
        state["tweeted_author"] = []

    author_index_to_tweet, updated_tweeted_authors = select_new_random_item(
        choices=options["config"]["authors"],
        previously_chosen=state["tweeted_author"]
    )

    # put it all together
    quote = options["config"]["quotes"][quote_index_to_tweet]
    author = options["config"]["authors"][author_index_to_tweet]
    tweet_text = f"'{quote}' - {author}"

    # send it
    result = api.send_tweet(tweet_text)

    if result.id:
        state["tweeted_quote"] = updated_tweeted_quotes
        state["tweeted_author"] = updated_tweeted_authors
        logger.info(f"Sent tweet ID {result.id} with text '{tweet_text}'")
    else:
        logger.error(f"Failed to send tweet index {tweet_indexes}: {result}")

    return state
