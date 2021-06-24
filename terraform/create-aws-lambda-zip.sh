#!/bin/bash

set -e

find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -delete

rm -f lambda.zip

# Only recreate the python-packages dir if it doesn't exist
if [ ! -d "python-packages" ]; then
  OS=$(uname -s)
  if [ "$OS" == "Darwin" ]; then
    # Must use docker to get python requirements otherwise the function won't run on AWS Lambda
    echo "Running on Mac"
    docker run -it --volume=$PWD/..:/temp python:3.8 bash -c 'pip install -r /temp/requirements.txt --target=/temp/terraform/python-packages'
  else
    echo "Running on Linux"
    pip install -r ../requirements.txt --target=python-packages
  fi
fi

zip -q -9 -r lambda.zip bot-config.yaml python-packages/
cd ..
zip -q -9 -r -u terraform/lambda.zip main.py serverless_twitter_bot
cd -

echo "AWS Lambda zip file created"
