# -*- coding: utf-8 -*-

import logging
import datetime
import random
import io
import requests
from serverless_twitter_bot import list_files, load_image_file, select_new_random_item
from tweepy import Cursor
from PIL import Image


# disable PIL debug logs
pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)


logger = logging.getLogger()


def run(api: object, options: dict, state: dict, recipient: str):
    recent_tweet = api.get_most_recent_tweet(recipient)

    if not recent_tweet:
        logger.info(f"No recent tweet for user {recipient}")
        return state

    recent_tweet_age = datetime.datetime.now() - recent_tweet.created_at
    if recent_tweet_age.seconds > 10800:
        logger.info(f"Recent tweet too old for tweet ID {recent_tweet.id}, user {recipient}")
        return state

    # select tweet text at random
    if "tweeted_text" not in state:
        state["tweeted_text"] = []

    replies = Cursor(api.api.search, q='to:{} filter:replies conversation_id:{}'.format(recipient, recent_tweet.id), tweet_mode='extended').items()

    if "users_replied_to" not in state:
        state["users_replied_to"] = []

    im = None

    for i in range(20):
        try:
            reply = replies.next()
        except StopIteration:
            break

        if reply.user.default_profile_image:
            logger.debug(f"Default profile image for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        age = datetime.datetime.now() - reply.created_at
        if age.seconds > 10800:
            logger.debug(f"Tweet too old for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        if reply.user.followers_count < 30:
            logger.debug(f"Followers count too low for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        if reply.user.friends_count < 30:
            logger.debug(f"Friend count too low for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        if reply.user.statuses_count < 1000:
            logger.debug(f"Status count too low for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        if reply.user.id in state["users_replied_to"]:
            logger.debug(f"Already replied to user for tweet ID {reply.id}, user {reply.user.screen_name}")
            continue

        im = Image.open(requests.get(reply.user.profile_image_url_https.replace('_normal.', '.'), stream=True).raw)
        im = im.resize((1200, 1200), Image.ANTIALIAS)
        break

    if not im:
        logger.error(f"No suitable reply found to tweet ID {recent_tweet.id} from {recent_tweet.user.screen_name}")
        return state

    logger.debug(f"Replying to {reply.id}, user {reply.user.screen_name}")

    # select 4 images at random
    path = options["config"]["images"]["path"]
    images = list_files(path)
    images = random.sample(images, 4)
    image_locations = [
        (10, 10),
        (10, 850),
        (800, 10),
        (800, 850),
    ]

    # overlay the images onto the profile image
    for i in range(4):
        overlay_image_bytes = load_image_file(images[i])
        overlay_image = Image.open(overlay_image_bytes)
        overlay_image.thumbnail((400, 400), Image.ANTIALIAS)
        try:
            im.paste(overlay_image, image_locations[i], overlay_image)
        except Exception as e:
            logger.info(f"Problem creating image with file {images[i]}")
            raise

    # create a file object to use for the reply
    f = io.BytesIO()
    im.save(f, "JPEG")
    f.seek(0)

    index_to_tweet, already_tweeted = select_new_random_item(
        choices=options["config"]["tweets"],
        previously_chosen=state["tweeted_text"]
    )
    tweet_text = options["config"]["tweets"][index_to_tweet]

    if options["config"].get("mention"):
        real_tweet_text = f"Hi @{reply.user.screen_name}, {tweet_text}"
    else:
        real_tweet_text = f"Hi there, {tweet_text}"

    result = api.reply_to_tweet_with_media(
        reply_tweet_id=reply.id,
        filename="great_profile_pic.jpeg",
        file=f,
        text=real_tweet_text,
    )

    if result.id:
        state["users_replied_to"].append(reply.user.id)
        state["tweeted_text"] = already_tweeted

        logger.info(f"Replied to tweet ID {reply.id}, reply ID is {result.id}")

        if options["config"].get("like_tweets"):
            like_result = api.like_tweet(reply.id)
            logger.info(f"Liked tweet ID {reply.id}, from {reply.user.screen_name}")

        if options["config"].get("follow_users"):
            follow_result = api.follow_user(screen_name=reply.user.screen_name)
            logger.info(f"Followed {reply.user.screen_name}")

    else:
        logger.error(f"Failed to send tweet: {result}")

    return state
