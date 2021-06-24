# -*- coding: utf-8 -*-

import os
import sys
import logging


def create_logger(suppress_package_logs=True):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
        pass
    else:
        stdout_format = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s %(filename)s:%(lineno)-12s %(message)s", "%Y-%m-%d %H:%M:%S")
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(stdout_format)
        stdout_handler.setLevel(logging.DEBUG)
        logger.addHandler(stdout_handler)

    if suppress_package_logs:
        logging.getLogger('boto3').setLevel(logging.CRITICAL)
        logging.getLogger('botocore').setLevel(logging.CRITICAL)
        logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
        logging.getLogger('urllib3').setLevel(logging.CRITICAL)
        logging.getLogger('tweepy').setLevel(logging.CRITICAL)
        logging.getLogger('requests_oauthlib').setLevel(logging.CRITICAL)
        logging.getLogger('oauthlib').setLevel(logging.CRITICAL)

    return logger
