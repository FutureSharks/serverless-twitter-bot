# -*- coding: utf-8 -*-

import boto3
import pickle
import os
import logging
import yaml
import datetime
import random
import serverless_twitter_bot
from botocore.exceptions import ClientError
from mergedeep import merge
from .twitter import Twitter


s3_client = boto3.client('s3')
logger = logging.getLogger()


class Bot(object):
    '''
    Represents a Bot
    '''
    def __init__(self):
        self.config_file = os.getenv('BOT_CONFIG_FILE', "bot-config.yaml")

        with open(self.config_file, 'r') as stream:
            self.config = yaml.safe_load(stream)

        self.state = serverless_twitter_bot.State(self.config["modes"].keys())
        self.rate_limited = self.state.bot_rate_limited(self.config.get("rate_limit"))
        logger.info(f"Config and state loaded for bot {self.config['name']}")

        self.twitter = Twitter()

    def _get_recipients(self, recipients, recipient_choice: dict):
        if type(recipients) is dict:
            recipients = list(recipients.keys())

        if recipient_choice == None:
            return random.sample(recipients, 1)

        if recipient_choice.get("all"):
            return recipients

        if recipient_choice.get("random"):
            return random.sample(recipients, recipient_choice["random"])

        raise

    def generate_rate_limit_config(self, config: dict=None):
        default_blank_config = {
            "type": None,
            "time": None,
            "time_fuzz": None,
            "scope": None,
        }

        if config == None:
            return default_blank_config
        else:
            return merge({}, default_blank_config, config)

    def run_modes(self):
        """
        Runs through all modes configured for the bot
        """
        self.state.update_bot_last_run()

        for mode_name, mode_options in self.config["modes"].items():
            logger.info(f'Starting mode {mode_name}')

            rate_limit_config = self.generate_rate_limit_config(mode_options.get("rate_limit"))

            if self.state.mode_rate_limited(mode_name, rate_limit_config):
                logger.info(f'Mode {mode_name} is rate limited')
                continue

            bot_functions = __import__('serverless_twitter_bot.bot_functions', fromlist=[mode_options["function"]])
            mode_object = getattr(bot_functions, mode_options["function"])
            self.state.update_mode_last_run(mode_name, rate_limit_config["time_fuzz"])

            if "recipients" in mode_options:
                mode_recipients = self._get_recipients(mode_options["recipients"], mode_options.get("recipient_choice"))
                for user in mode_recipients:
                    if self.state.user_rate_limited(user, rate_limit_config):
                        logger.info(f'User {user} is currently rate limited')
                        continue
                    else:
                        logger.info(f'Running mode {mode_name} for user {user}')
                        mode_state = self.state.get_mode_state(mode_name)
                        new_mode_state = mode_object.run(api=self.twitter, options=mode_options, recipient=user, state=mode_state)
                        self.state.update_user_last_interaction(user, rate_limit_config["time_fuzz"])
                        self.state.save_mode_state(mode_name=mode_name, state=new_mode_state)
            else:
                mode_state = self.state.get_mode_state(mode_name)
                new_mode_state = mode_object.run(api=self.twitter, options=mode_options, state=mode_state)
                self.state.save_mode_state(mode_name=mode_name, state=new_mode_state)

        return
