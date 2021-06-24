# -*- coding: utf-8 -*-

import logging
import datetime
from os import listdir
from os.path import isfile, join
from serverless_twitter_bot import select_new_random_item, list_files, load_image_file


logger = logging.getLogger()


def run(api: object, options: dict, state: dict, recipient: str):
    recent_tweet = api.get_most_recent_tweet(recipient)

    # check tweet age
    age = datetime.datetime.now() - recent_tweet.created_at
    if age.seconds > options["config"].get("tweet_age_limit", 108000):
        logger.info(f"Tweet ID {recent_tweet.id} is too old")
        return state

    # check if is a reply
    if recent_tweet.in_reply_to_status_id:
        logger.info(f"Tweet ID {recent_tweet.id} is a reply")
        return state

    # check if we have replied to this tweet
    if "already_replied_to" not in state:
        state["already_replied_to"] = []

    if recent_tweet.id in state["already_replied_to"]:
        logger.info(f"Already replied to tweet ID {recent_tweet.id}")
        return state

    # select a tweet at random
    if "tweets" in options["config"]:
        if "already_tweeted" not in state:
            state["already_tweeted"] = []

        index_to_tweet, already_tweeted = select_new_random_item(
            choices=options["config"]["tweets"],
            previously_chosen=state["already_tweeted"]
        )

        tweet_text = options["config"]["tweets"][index_to_tweet]
    else:
        tweet_text = None

    # select an image at random
    if "images" in options["config"]:
        path = options["config"]["images"]["path"]
        images = list_files(path)

        if "tweeted_images" not in state:
            state["tweeted_images"] = []

        image_index_to_tweet, image_already_tweeted = select_new_random_item(
            choices=images,
            previously_chosen=state["tweeted_images"]
        )

        image_path = images[image_index_to_tweet]
        image = load_image_file(image_path)
    else:
        image_path = None

    # put it all together, send it
    if image_path:
        result = api.reply_to_tweet_with_media(
            reply_tweet_id=recent_tweet.id,
            file=image,
            filename="file.jpeg",
            text=tweet_text,
        )
    else:
        result = api.reply_to_tweet(
            reply_tweet_id=recent_tweet.id,
            text=tweet_text,
        )

    if result.id:
        state["already_replied_to"].append(result.id)

        if "tweets" in options["config"]:
            state["tweeted_text"] = already_tweeted

        if "images" in options["config"]:
            state["tweeted_images"] = image_already_tweeted

        logger.info(f"Replied to tweet ID {recent_tweet.id}, reply ID is {result.id} with text '{tweet_text}' and image {image_path}")
    else:
        logger.error(f"Failed to send tweet index {tweet_indexes}: {result}")

    return state
