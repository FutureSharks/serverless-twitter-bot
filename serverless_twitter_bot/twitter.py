# -*- coding: utf-8 -*-

import os
import tweepy
import logging
from typing import BinaryIO


logger = logging.getLogger()


class Twitter(object):
    '''
    Represents the Twitter API
    '''
    def __init__(self):
        self.test_mode = os.getenv('TWITTER_TEST_MODE', "False").lower() in ['true', '1']

        if self.test_mode:
            logger.info("Twitter is in test mode")
        else:
            self.auth = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_SECRET'])
            self.auth.set_access_token(os.environ['TWITTER_ACCESS_TOKEN'], os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
            self.api = tweepy.API(
                self.auth,
                wait_on_rate_limit=True,
                wait_on_rate_limit_notify=True,
                retry_count=5,
                retry_delay=10,
            )
            if not self.test_api():
                raise("Twitter API not working")

    def test_api(self):
        """
        Gets own account to test API access is working
        """
        me = self.api.me()
        if me.screen_name:
            return True
        else:
            return False

    def get_most_recent_tweet(self, user: str):
        if self.test_mode:
            return TweepyTestStatus()
        else:
            results = self.api.user_timeline(screen_name=user, count=1, exclude_replies=True, include_rts=False)
            if results:
                return results[0]
            else:
                return None

    def send_tweet(self, text: str):
        if self.test_mode:
            return TweepyTestStatus()
        else:
            return self.api.update_status(text)

    def follow_user(self, screen_name: str):
        if self.test_mode:
            return tweepy.models.User()
        else:
            return self.api.create_friendship(screen_name=screen_name)

    def like_tweet(self, tweet_id):
        if self.test_mode:
            result = TweepyTestStatus()
            result.favorited = True
            return result
        else:
            return self.api.create_favorite(tweet_id)

    def retweet_tweet(self, tweet_id):
        if self.test_mode:
            result = TweepyTestStatus()
            result.retweeted = True
            return result
        else:
            return self.api.retweet(tweet_id)

    def send_tweet_with_media(self, filename: str, file: BinaryIO, text: str = None):
        if self.test_mode:
            return TweepyTestStatus()
        else:
            return self.api.update_with_media(
                filename=filename,
                file=file,
                status=text,
                auto_populate_reply_metadata=True
            )

    def reply_to_tweet(self, reply_tweet_id: int, text: str):
        if self.test_mode:
            return TweepyTestStatus()
        else:
            return self.api.update_status(
                status=text,
                in_reply_to_status_id=reply_tweet_id,
                auto_populate_reply_metadata=True
            )

    def reply_to_tweet_with_media(self, reply_tweet_id: int, filename: str, file: BinaryIO, text: str = None):
        if self.test_mode:
            return TweepyTestStatus()
        else:
            return self.api.update_with_media(
                status=text,
                filename=filename,
                file=file,
                in_reply_to_status_id=reply_tweet_id,
                auto_populate_reply_metadata=True,
            )


class TweepyTestStatus(tweepy.models.Status):
    """
    A Tweepy Test status. Just used for tests.
    """
    def __init__(self):
        self.id = 666666666
        self.favorited = False
        self.retweeted = False
        self.user = tweepy.models.User()
        self.user.screen_name = "test_user"
