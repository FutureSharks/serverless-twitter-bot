# -*- coding: utf-8 -*-

import boto3
import pickle
import os
import logging
import yaml
import datetime
import random
from botocore.exceptions import ClientError
from mergedeep import merge
from .helpers import str_to_datetime


s3_client = boto3.client('s3')
logger = logging.getLogger()


class State(object):
    """
    The state of the bot
    """
    default_state = {
        "last_run": None,
        "rate_limit": {},
        "modes": {},
        "recipients": {},
    }
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

    def __init__(self, modes: list=[]):
        self.test_mode = os.getenv('STATE_TEST_MODE', "False").lower() in ['true', '1']
        self.print_state = os.getenv('STATE_PRINT', "False").lower() in ['true', '1']
        self.modes = modes
        self._override_current_time = None

        if self.test_mode:
            self.load_test_state()
        else:
            self.state_s3_bucket = os.environ['STATE_S3_BUCKET']
            self.state_s3_key = os.environ['STATE_S3_KEY']
            self.load_s3_state()

    def _generate_defult_state(self):
        s = self.default_state.copy()

        for mode in self.modes:
            s["modes"][mode] = {}
            s["modes"][mode]["state"] = {}
            s["modes"][mode]["last_run"] = None

        return s

    def _now(self):
        if self.test_mode:
            if self._override_current_time:
                return self._override_current_time
            else:
                return datetime.datetime.utcnow()
        else:
            return datetime.datetime.utcnow()

    def load_s3_state(self):
        self.state = self._generate_defult_state()

        logger.debug(f"Loading state from {self.state_s3_bucket}/{self.state_s3_key}")

        try:
            object = s3_client.get_object(Bucket=self.state_s3_bucket, Key=self.state_s3_key)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.info(f"No S3 key at {self.state_s3_bucket}/{self.state_s3_key}, will start with blank state")
            else:
                raise
        else:
            serializedObject = object['Body'].read()
            if len(serializedObject) == 0:
                logger.info("State file is 0 szie, will start with blank state")
            else:
                self.state = merge({}, self.state, pickle.loads(serializedObject))

        if self.print_state:
            logger.debug(f"State loaded from S3: {self.state}")
        else:
            logger.debug("State loaded from S3")

    def load_test_state(self):
        self.state = self._generate_defult_state()
        logger.debug("Loading test state")
        if self.print_state:
            logger.debug(f"State loaded: {self.state}")
        else:
            logger.debug("State loaded")

    def save_state(self):
        if self.print_state:
            logger.debug(f"Saving state: {self.state}")
        else:
            logger.debug("Saving state")

        if self.test_mode:
            return
        else:
            serializedObject = pickle.dumps(self.state)
            result = s3_client.put_object(Body=serializedObject, Bucket=self.state_s3_bucket, Key=self.state_s3_key)

    def _create_fuzzed_timestamp(self, time_fuzz: str) -> str:
        random_seconds = random.randrange(1, self._convert_to_seconds(time_fuzz))
        last_run_adjusted = self._now() - datetime.timedelta(seconds=random_seconds)
        return str(last_run_adjusted)

    def update_bot_last_run(self, time_fuzz: str=None):
        logger.debug("Updating bot last_run")

        if time_fuzz:
            last_run_time = self._create_fuzzed_timestamp(time_fuzz)
        else:
            last_run_time = str(self._now())

        self.state["last_run"] = last_run_time
        self.save_state()

    def update_mode_last_run(self, mode: str, time_fuzz: str=None):
        logger.debug(f"Updating last_run for mode {mode}")

        if time_fuzz:
            last_run_time = self._create_fuzzed_timestamp(time_fuzz)
        else:
            last_run_time = str(self._now())

        self.state["modes"][mode]["last_run"] = last_run_time
        self.save_state()

    def update_user_last_interaction(self, user: str, time_fuzz: str=None):
        logger.debug(f"Updating last_interaction for user {user}")

        if time_fuzz:
            last_run_time = self._create_fuzzed_timestamp(time_fuzz)
        else:
            last_run_time = str(self._now())

        if user not in self.state["recipients"]:
            self.state["recipients"][user] = {}

        self.state["recipients"][user]["last_interaction"] = last_run_time
        self.save_state()

    def _convert_to_seconds(self, s: str) -> int:
        """
        Converts a time string to seconds
        """
        return int(s[:-1]) * self.seconds_per_unit[s[-1]]

    def _check_rate_limit(self, last_run_str: str, t: str):
        if last_run_str == None:
            return False

        last_run = str_to_datetime(last_run_str)
        time_since = self._now() - last_run

        if time_since.total_seconds() > self._convert_to_seconds(t):
            return False
        else:
            return True

    def get_mode_state(self, mode_name: str):
        """
        Gets saved state for a mode
        """
        return self.state["modes"][mode_name]["state"]

    def save_mode_state(self, mode_name: str, state: dict):
        """
        Saves a state for a mode
        """
        self.state["modes"][mode_name]["state"] = state
        self.save_state()

    def bot_rate_limited(self, rate_limit_config: dict):
        """
        Checks to see if whole bot is rate limited
        """
        logger.debug("Checking bot rate limit")

        if rate_limit_config == None:
            return False

        if self.state.get("last_run") == None:
            return False

        if rate_limit_config.get("type") != "global":
            return False

        return self._check_rate_limit(self.state["last_run"], rate_limit_config["time"])

    def mode_rate_limited(self, mode_name: str, rate_limit_config: dict):
        """
        Checks to see if a mode is currently rate limited
        """
        logger.debug(f"Checking rate limit for mode {mode_name}")

        if rate_limit_config.get("type") != "per_mode":
            return False

        if self.state["modes"][mode_name].get("last_run") == None:
            return False

        if rate_limit_config.get("time") == None:
            return False

        return self._check_rate_limit(self.state["modes"][mode_name].get("last_run"), rate_limit_config["time"])

    def user_rate_limited(self, user: str, rate_limit_config: dict):
        """
        Checks to see if a user is currently rate limited
        """
        logger.debug(f"Checking rate limit for user {user}")

        if rate_limit_config == None:
            return False

        if rate_limit_config.get("type") != "per_recipient":
            return False

        if rate_limit_config.get("time") == None:
            return False

        if user not in self.state["recipients"]:
            return False

        return self._check_rate_limit(self.state["recipients"][user].get("last_interaction"), rate_limit_config["time"])
