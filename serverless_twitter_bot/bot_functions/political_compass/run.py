# -*- coding: utf-8 -*-

import logging
import datetime
import random
import io
import requests
import matplotlib.pyplot as plt
from serverless_twitter_bot import list_files, load_image_file, select_new_random_item
from PIL import Image, ImageOps


logger = logging.getLogger()


def run(api: object, options: dict, state: dict, recipient: str):
    recent_tweet = api.get_most_recent_tweet(recipient)

    if not recent_tweet:
        logger.info(f"No recent tweet for user {recipient}")
        return state

    recent_tweet_age = datetime.datetime.utcnow() - recent_tweet.created_at

    if recent_tweet_age.seconds > 90800:
        logger.info(f"Recent tweet too old for tweet ID {recent_tweet.id}, user {recipient}")
        return state

    if "tweeted_text" not in state:
        state["tweeted_text"] = []

    if "tweets_replied_to" not in state:
        state["tweets_replied_to"] = []

    if recent_tweet.id in state["tweets_replied_to"]:
        logger.info(f"Already replied to tweet ID {recent_tweet.id}, user {recipient}")
        return state

    # Create the base compass image
    fig = plt.figure(figsize=(17, 17))
    fig.set_facecolor('white')
    plt.plot([round(random.uniform(-1, 1), 1)], [round(random.uniform(-1, 1), 1)], 'rX', markersize=40)
    plt.ylim(-1.1, 1.1)
    plt.xlim(-1.1, 1.1)
    plt.axhline(0, color='black', linewidth=4)
    plt.axvline(0, color='black', linewidth=4)
    plt.box(False)
    plt.axis('off')
    # Save it as PIL Image
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    im = Image.open(buf)
    im = ImageOps.expand(im, border=200, fill='white')
    im = im.resize((1200, 1200), Image.ANTIALIAS)

    logger.debug(f"Replying to {recent_tweet.id}, user {recent_tweet.user.screen_name}")

    # select 4 images at random
    path = options["config"]["images"]["path"]
    images = list_files(path)
    images = random.sample(images, 4)
    image_locations = [
        (450, 10),
        (450, 950),
        (10, 450),
        (900, 548),
    ]

    # overlay the images onto the compass image
    for i in range(4):
        overlay_image_bytes = load_image_file(images[i])
        overlay_image = Image.open(overlay_image_bytes).convert("RGBA")
        overlay_image.thumbnail((400, 400), Image.ANTIALIAS)
        try:
            im.paste(overlay_image, image_locations[i], overlay_image)
        except Exception as e:
            logger.info(f"Problem creating image with file {images[i]}")
            raise

    # create a file object to use for the reply
    f = io.BytesIO()
    im = im.convert("RGB")
    im.save(f, "JPEG")
    f.seek(0)

    index_to_tweet, already_tweeted = select_new_random_item(
        choices=options["config"]["tweets"],
        previously_chosen=state["tweeted_text"]
    )
    tweet_text = options["config"]["tweets"][index_to_tweet]

    if options["config"].get("mention"):
        real_tweet_text = f"Hi @{recent_tweet.user.screen_name}, {tweet_text}"
    else:
        real_tweet_text = f"Hi there, {tweet_text}"

    result = api.reply_to_tweet_with_media(
        reply_tweet_id=recent_tweet.id,
        filename="great_political_compass.jpeg",
        file=f,
        text=real_tweet_text,
    )

    if result.id:
        state["tweeted_text"] = already_tweeted
        state["tweets_replied_to"].append(recent_tweet.id)
        logger.info(f"Replied to tweet ID {recent_tweet.id}, reply ID is {result.id}")
    else:
        logger.error(f"Failed to send tweet: {result}")

    return state
