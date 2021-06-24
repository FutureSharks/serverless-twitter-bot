# -*- coding: utf-8 -*-

import datetime
import boto3
import os
from random import choice
from typing import List, Set, Dict, Tuple, Optional, BinaryIO
from PIL import Image
from urllib.parse import urlparse
from io import BytesIO

def select_new_random_item(choices, previously_chosen: List=[int]) -> Tuple[int, list]:
    """
    Used to select random items from a list or map without repeating

    choices: a list or dict of items to choose from
    previously_chosen: a list of index that have already been previously selected
    """
    def _create_indexes(choices):
        if isinstance(choices, list):
            return list(range(len(choices)))
        else:
            return list(range(len(choices.keys())))

    choice_indexes = _create_indexes(choices)

    for i in previously_chosen:
        try:
            choice_indexes.remove(i)
        except ValueError:
            pass

    if len(choice_indexes) == 0:
        previously_chosen = []
        choice_indexes = _create_indexes(choices)

    chosen_index = choice(choice_indexes)
    previously_chosen.append(chosen_index)

    return (chosen_index, previously_chosen)


def str_to_datetime(date_string: str) -> datetime.datetime:
    """
    Parses a string and returns a datetime object
    """
    return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")


def list_files(path: str):
    """
    Gets list of files at a path whether it's local or on S3
    """
    if path.startswith("s3://"):
        parsed_url = urlparse(path)
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(parsed_url.netloc)
        s3_files = [f"s3://{parsed_url.netloc}/{obj.key}" for obj in bucket.objects.filter(Prefix=parsed_url.path.lstrip("/"))]
        return s3_files
    else:
        files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        return files


def load_image_file(path: str) -> BinaryIO:
    """
    Loads an image file whether it's local or on S3
    """
    if path.startswith("s3://"):
        parsed_url = urlparse(path)
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(parsed_url.netloc)
        obj = bucket.Object(parsed_url.path.lstrip("/"))
        file = BytesIO()
        obj.download_fileobj(file)
    else:
        with open(path, 'rb') as fh:
            file = BytesIO(fh.read())

    file.seek(0)
    
    return file
