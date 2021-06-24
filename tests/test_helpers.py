from unittest import TestCase
from serverless_twitter_bot import select_new_random_item, list_files, load_image_file


class TestSelectNewRandomItem(TestCase):
    def test_with_list(self):
        choices = ["c1", "c2", "c3", "c4"]
        previously_chosen = []

        for i in range(len(choices)):
            chosen_item, previously_chosen = select_new_random_item(
                choices=choices,
                previously_chosen=previously_chosen,
            )

            assert type(chosen_item) == int
            assert chosen_item <= len(choices) - 1
            assert len(previously_chosen) == 1 + i
            assert chosen_item in previously_chosen


        chosen_item, previously_chosen = select_new_random_item(
            choices=choices,
            previously_chosen=previously_chosen,
        )

        assert len(previously_chosen) == 1

    def test_with_dict(self):
        choices = {
            "c1": None,
            "c2": None,
            "c3": None,
            "c4": None,
        }
        previously_chosen = []

        for i in range(len(choices)):
            chosen_item, previously_chosen = select_new_random_item(
                choices=choices,
                previously_chosen=previously_chosen,
            )

            assert type(chosen_item) == int
            assert chosen_item <= len(choices.keys()) - 1
            assert len(previously_chosen) == 1 + i
            assert chosen_item in previously_chosen

        chosen_item, previously_chosen = select_new_random_item(
            choices=choices,
            previously_chosen=previously_chosen,
        )

        assert len(previously_chosen) == 1


class TestListFiles(TestCase):
    def test_with_local_files(self):
        files = list_files("img")
        assert len(files) == 2


class TestLoadImageFile(TestCase):
    def test_with_local_files(self):
        image = load_image_file("tests/test_image_aws_logo.png")
        assert image.getbuffer().nbytes == 12182
