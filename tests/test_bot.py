import time
import os
from unittest import TestCase
from serverless_twitter_bot import Bot
from datetime import datetime, timedelta


class TestBot(TestCase):
    os.environ["STATE_TEST_MODE"] = "1"
    os.environ["TWITTER_TEST_MODE"] = "1"
    os.environ["BOT_CONFIG_FILE"] = "tests/test-bot-config.yaml"

    def test_initialisation(self):
        bot = Bot()

        assert len(bot.state.state["modes"]) == len(bot.config["modes"])
        assert bot.rate_limited != True

    def test_run(self):
        bot = Bot()
        last_run_state = {}

        def _save_last_runs():
            for mode in bot.config["modes"].keys():
                # Check that last_run in state has been updated
                assert type(bot.state.state["modes"][mode]["last_run"]) is str
                # Save all last_run times in a separate dict
                last_run_state[mode] = bot.state.state["modes"][mode]["last_run"]


        # First run
        bot.run_modes()
        # Ensure correct amount of users have had last_interaction updated
        assert len(bot.state.state["recipients"].keys()) == 5

        # Second run
        time.sleep(1)
        _save_last_runs()
        # Ensure all modes have run
        assert len(bot.config["modes"].keys()) == len(last_run_state.keys())
        bot.run_modes()
        # These modes should all be rate limited so should not run
        assert bot.state.state["modes"]["test_mode_1"]["last_run"] == last_run_state["test_mode_1"]
        assert bot.state.state["modes"]["test_mode_5"]["last_run"] == last_run_state["test_mode_5"]
        assert bot.state.state["modes"]["test_mode_6"]["last_run"] == last_run_state["test_mode_6"]
        # This mode has no rate limit so should run
        assert bot.state.state["modes"]["test_mode_2"]["last_run"] != last_run_state["test_mode_2"]
        # Ensure correct amount of users have had last_interaction updated
        assert len(bot.state.state["recipients"].keys()) > 5


        # Fast forward time and rerun bot
        bot.state._override_current_time = datetime.now() + timedelta(hours=6)
        _save_last_runs()
        bot.run_modes()
        # These modes should all be rate limited so should not run
        assert bot.state.state["modes"]["test_mode_1"]["last_run"] == last_run_state["test_mode_1"]
        assert bot.state.state["modes"]["test_mode_5"]["last_run"] == last_run_state["test_mode_5"]
        # This mod should now run
        assert bot.state.state["modes"]["test_mode_6"]["last_run"] != last_run_state["test_mode_6"]
        # This mode has no rate limit so should run
        assert bot.state.state["modes"]["test_mode_2"]["last_run"] != last_run_state["test_mode_2"]


        # Fast forward time and rerun bot
        bot.state._override_current_time = datetime.now() + timedelta(days=1)
        _save_last_runs()
        bot.run_modes()
        # This mode has no rate limit so should run
        assert bot.state.state["modes"]["test_mode_2"]["last_run"] != last_run_state["test_mode_2"]
        # These modes should all be rate limited so should not run
        assert bot.state.state["modes"]["test_mode_5"]["last_run"] == last_run_state["test_mode_5"]
        # This mod should now run
        assert bot.state.state["modes"]["test_mode_1"]["last_run"] != last_run_state["test_mode_1"]
        assert bot.state.state["modes"]["test_mode_6"]["last_run"] != last_run_state["test_mode_6"]


        # Fast forward time and rerun bot
        bot.state._override_current_time = datetime.now() + timedelta(days=13)
        _save_last_runs()
        bot.run_modes()
        # This mode has no rate limit so should run
        assert bot.state.state["modes"]["test_mode_2"]["last_run"] != last_run_state["test_mode_2"]
        # This mod should now run
        assert bot.state.state["modes"]["test_mode_1"]["last_run"] != last_run_state["test_mode_1"]
        assert bot.state.state["modes"]["test_mode_6"]["last_run"] != last_run_state["test_mode_6"]
        assert bot.state.state["modes"]["test_mode_5"]["last_run"] != last_run_state["test_mode_5"]
