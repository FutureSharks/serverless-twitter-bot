import datetime
import time
import os
from unittest import TestCase
from serverless_twitter_bot import State, str_to_datetime


modes = ["mode_1", "mode_2", "mode_3"]


class TestState(TestCase):
    os.environ["STATE_TEST_MODE"] = "1"

    def test_initialisation(self):
        state = State(modes=modes)

        assert state.modes == modes
        assert state.state["modes"]["mode_1"]["state"] == {}
        assert state.state["modes"]["mode_2"]["last_run"] == None

    def test_last_run(self):
        state = State(modes=modes)

        state.update_bot_last_run()
        assert type(state.state["last_run"]) == str
        delta = datetime.datetime.utcnow() - str_to_datetime(state.state["last_run"])
        assert delta.seconds < 1

        state.update_mode_last_run(mode="mode_1")
        assert type(state.state["modes"]["mode_1"]["last_run"]) == str
        delta = datetime.datetime.utcnow() - str_to_datetime(state.state["modes"]["mode_1"]["last_run"])
        assert delta.seconds < 1

        state.update_user_last_interaction(user="user1")
        assert type(state.state["recipients"]["user1"]["last_interaction"]) == str
        delta = datetime.datetime.utcnow() - str_to_datetime(state.state["recipients"]["user1"]["last_interaction"])
        assert delta.seconds < 1

    def test_mode_state(self):
        state = State(modes=modes)

        assert state.get_mode_state("mode_1") == {}

        test_mode_state = {
            "tweeted_author": [1],
            "tweeted_images": [3]
        }
        state.save_mode_state("mode_1", test_mode_state)
        assert "tweeted_author" in state.get_mode_state("mode_1").keys()
        assert "tweeted_images" in state.get_mode_state("mode_1").keys()
        assert state.get_mode_state("mode_1")["tweeted_images"] == [3]

    def test_bot_rate_limit(self):
        state = State(modes=modes)
        state.update_bot_last_run()
        time.sleep(5)

        rate_limit_config = {}
        assert state.bot_rate_limited(rate_limit_config) == False

        rate_limit_config["time"] = "3s"
        assert state.bot_rate_limited(rate_limit_config) == False

        rate_limit_config["time"] = "10s"
        rate_limit_config["type"] = "global"
        assert state.bot_rate_limited(rate_limit_config) == True

    def test_mode_rate_limit(self):
        state = State(modes=modes)
        rate_limit_config = {}

        assert state.mode_rate_limited(mode_name="mode_1", rate_limit_config=rate_limit_config) == False

        rate_limit_config["type"] = "per_mode"
        assert state.mode_rate_limited(mode_name="mode_1", rate_limit_config=rate_limit_config) == False

        state.update_mode_last_run(mode="mode_1")
        time.sleep(5)

        assert state.mode_rate_limited(mode_name="mode_1", rate_limit_config=rate_limit_config) == False

        rate_limit_config["time"] = "3s"
        assert state.mode_rate_limited(mode_name="mode_1", rate_limit_config=rate_limit_config) == False

        rate_limit_config["time"] = "10s"
        assert state.mode_rate_limited(mode_name="mode_1", rate_limit_config=rate_limit_config) == True

    def test_user_rate_limit(self):
        state = State(modes=modes)
        rate_limit_config = {}

        assert state.user_rate_limited(user="user_1", rate_limit_config=rate_limit_config) == False

        rate_limit_config["type"] = "per_recipient"
        assert state.user_rate_limited(user="user_1", rate_limit_config=rate_limit_config) == False

        state.update_user_last_interaction(user="user_1")
        time.sleep(5)

        assert state.user_rate_limited(user="user_1", rate_limit_config=rate_limit_config) == False

        rate_limit_config["time"] = "3s"
        assert state.user_rate_limited(user="user_1", rate_limit_config=rate_limit_config) == False

        rate_limit_config["time"] = "10s"
        assert state.user_rate_limited(user="user_1", rate_limit_config=rate_limit_config) == True
        assert state.user_rate_limited(user="user_does_not_exist", rate_limit_config=rate_limit_config) == False

    def test_time_fuzz(self):
        state = State(modes=modes)
        rate_limit_config = {}

        state.update_bot_last_run(time_fuzz="3h")
        assert type(state.state["last_run"]) == str
        delta = datetime.datetime.utcnow() - str_to_datetime(state.state["last_run"])
        assert delta.seconds >= 1

        state.update_mode_last_run(mode="mode_1", time_fuzz="3h")
        assert type(state.state["modes"]["mode_1"]["last_run"]) == str
        delta = datetime.datetime.utcnow() - str_to_datetime(state.state["modes"]["mode_1"]["last_run"])
        assert delta.seconds >= 1

        state.update_user_last_interaction(user="user_2", time_fuzz="3h")
        assert type(state.state["recipients"]["user_2"]["last_interaction"]) == str
        delta = datetime.datetime.utcnow() - str_to_datetime(state.state["recipients"]["user_2"]["last_interaction"])
        assert delta.seconds >= 1
