# serverless-twitter-bot

[![](img/aws-lambda-logo.jpg)](#) [![](img/twitter-logo.png)](#)

A Twitter bot that runs on AWS Lambda. The bot has a number of functions, called "modes", that can do the following actions:

- Like tweets from a list of users
- Retweet tweets from a list of users
- Reply with text randomly chosen from a list
- Reply with images randomly chosen from a list
- And more in [serverless_twitter_bot/bot_functions](serverless_twitter_bot/bot_functions)

Other features:

- Easy to add new modes for different functionality or behaviour
- Bot state is saved to an S3 bucket
- Images used in replies can be stored on S3 or locally
- Mode can save their own state to persist data after each run
- Rate limiting for the bot, per mode or per user interaction
- Written in Python 3
- Detailed logging

You will need to [create a Twitter developer account](https://developer.twitter.com/en/apply-for-access) and create a twitter application.

Example bot configuration:

```yaml
name: my-bot

modes:
  reply_to_friends:
    function: reply
    config:
      tweets:
        - 100% agree 💙
        - I miss you
    recipients:
      - BoJackHorseman

  like_tweets:
    function: like
    recipients:
      - NASAPersevere
      - archillect
      - horse_ebooks
    rate_limit:
      type: per_recipient
      time: 2d

  retweet:
    function: retweet
    recipients:
      - dril
      - Coldwar_Steve
    rate_limit:
      type: per_recipient
      time: 3d

  reply_to_idiots:
    function: reply
    config:
      tweets:
        - Are your parents cousins?
        - You are an embarrassment
    recipients:
      - DonaldJTrumpJr
```

## Installation and configuration

Configuration of the modes, rate limiting and other settings is in a simple YAML file. It's easiest to just look at the example: [terraform/bot-config.yaml](terraform/bot-config.yaml).

To create the AWS Lambda function and all associated resources it's easiest to use the provided Terraform code in [terraform](terraform).

## Running

Some environment variables are required for configuration of the bot:

- `BOT_CONFIG_FILE`: Path to the bot configuration file
- `STATE_S3_BUCKET`: The name of the S3 bucket to find/store the bot state
- `STATE_S3_KEY`: The name of the key in the S3 bucket to find the state file
- `AWS_REGION`: The AWS region
- `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`: These come from your Twitter app in the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)

### Locally

Install the required packages:

```
pip3 install -r requirements.txt
```

You can run it locally without AWS Lambda like this:

```
export PYTHONPATH=serverless_twitter_bot
python3 main.py
```

You can also install it locally:

```
pip3 install .
```

### Manually using AWS CLI

Run this:

```
aws lambda invoke --function-name my-bot-name out --log-type Tail --query 'LogResult' --output text |  base64 -d
```

### Manually using AWS Console

You can run a test invocation from the AWS Lambda console tab `Test`, the payload doesn't matter.

### On a schedule

The Terraform code has a `enable_schedule` variable to enable a schedule for running the AWS Lambda function.

## Running tests

First, adjust an env var:

```
export PYTHONPATH=serverless_twitter_bot
```

To run all tests, from root of repo run:

```
python3 -m unittest discover
```

Or to run a specific tests:

```
python3 -m unittest tests.test_bot.TestBot
```
