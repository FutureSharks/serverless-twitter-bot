from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="serverless_twitter_bot",
    version="0.1",
    author="Max Williams",
    author_email="futuresharks@gmail.com",
    description="A Twitter bot to run with Python or on AWS Lambda",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FutureSharks/serverless-twitter-bot",
    license="GPLv3",
    scripts=["main.py"],
    packages=[
        "serverless_twitter_bot",
        "serverless_twitter_bot.bot_functions",
    ],
    keywords=["twitter", "serverless", "lambda", "bot"],
)
