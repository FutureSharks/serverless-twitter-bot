# -*- coding: utf-8 -*-

import logging
from os import listdir
from os.path import isfile, join
from serverless_twitter_bot import select_new_random_item, list_files, load_image_file


logger = logging.getLogger()


def run(api: object, options: dict, state: dict):
    # select tweet text at random
    if "tweeted_text" not in state:
        state["tweeted_text"] = []

    index_to_tweet, already_tweeted = select_new_random_item(
        choices=options["config"]["tweets"],
        previously_chosen=state["tweeted_text"]
    )

    tweet_text = options["config"]["tweets"][index_to_tweet]

    # select an image at random
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

    # put it all together and send it
    result = api.send_tweet_with_media(text=tweet_text, file=image, filename="file.jpeg")

    if result.id:
        state["tweeted_text"] = already_tweeted
        state["tweeted_images"] = image_already_tweeted
        logger.info(f"Sent tweet ID {result.id} with text '{tweet_text}' and image {image_path}")
    else:
        logger.error(f"Failed to send tweet index {tweet_indexes} with image {image_path}: {result}")

    return state
