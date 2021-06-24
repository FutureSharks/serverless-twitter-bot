#!/usr/bin/env python3

import os
import sys
import argparse

if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    sys.path.insert(0, "python-packages")

import logging
import pprint
import serverless_twitter_bot


logger = serverless_twitter_bot.create_logger()
bot = serverless_twitter_bot.Bot()


def handler(event=None, context=None):
    if bot.rate_limited:
        logger.info('Global rate limit in effect')
        return True

    bot.run_modes()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A serverless twitter bot")
    parser.add_argument("-r", "--run", help="Run all bot modes", action='store_true', default=True)
    parser.add_argument("-s", "--print-state", help="Gets the state and prints it.", action='store_true', default=False)
    config = parser.parse_args()

    if config.print_state:
        logger.info("Print state from S3 bucket")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(bot.state.state)
    elif config.run:
        handler()
    else:
        pass
