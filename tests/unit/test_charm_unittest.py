# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

"""Test the charm using Harness with unittest."""

import time
import unittest
import unittest.mock

import fortune
import ops
import ops.testing
from charm import ActionsTestingCharm


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = ops.testing.Harness(ActionsTestingCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_simple(self):
        """Verify that the 'simple' action runs without error."""
        out = self.harness.run_action("simple")
        assert out.results is None
        assert out.logs == []
        assert not out.failure

    def test_input_default_value(self):
        """Verify that the 'input' action runs correctly (no arg is provided)."""
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("input")
        assert out.results is None
        assert out.logs == []
        assert not out.failure
        default_value = self.harness.charm.meta.actions["input"].parameters["arg"]
        self.assertEqual(cm.output, [f"INFO:charm:The 'input' action says: {default_value}"])

    def test_input(self):
        """Verify that the 'input' action runs correctly (an arg is provided)."""
        response = "hello"
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("input", {"arg": response})
        assert out.results is None
        assert out.logs == []
        assert not out.failure
        self.assertEqual(cm.output, [f"INFO:charm:The 'input' action says: {response}"])

    def test_multi_input_default_value(self):
        """Verify that the 'multi-input' action runs correctly (no arg is provided)."""
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("multi-input")
        assert out.results is None
        assert out.logs == []
        assert not out.failure
        defaults = self.harness.charm.meta.actions["input"].parameters
        self.assertEqual(
            cm.output, [f"INFO:charm:The 'multi-input' action says: {defaults['arg1']['default']}"]
        )

    def test_multi_input_arg1(self):
        """Verify that the 'multi-input' action runs correctly (arg1 is provided)."""
        response = "hello"
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("multi-input", params={"arg1": response})
        assert out.results is None
        assert out.logs == []
        assert not out.failure
        self.assertEqual(cm.output, [f"INFO:charm:The 'multi-input' action says: {response}"])

    def test_multi_input_arg2(self):
        """Verify that the 'multi-input' action runs correctly (arg2 is provided)."""
        count = 2
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("multi-input", params={"arg2": count})
        assert out.results is None
        assert out.logs == []
        assert not out.failure
        defaults = self.harness.charm.meta.actions["input"].parameters
        self.assertEqual(
            cm.output,
            [f"INFO:charm:The 'multi-input' action says: {defaults['arg1']['default']}"] * count,
        )

    def test_multi_input_arg1_and_arg2(self):
        """Verify that the 'multi-input' action runs correctly (arg1 and arg2 are provided)."""
        response = "hello"
        count = 3
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("multi-input", params={"arg1": response, "arg2": count})
        assert out.results is None
        assert out.logs == []
        assert not out.failure
        self.assertEqual(
            cm.output, [f"INFO:charm:The 'multi-input' action says: {response}"] * count
        )

    def test_output(self):
        """Verify that the 'output' action runs correctly."""
        my_fortune = "favours the brave"
        with unittest.mock.patch.object(fortune, "get_random_fortune", return_value=my_fortune):
            out = self.harness.run_action("output")
        assert out.results == {"fortune": my_fortune}
        assert out.logs == []
        assert not out.failure

    def test_logger(self):
        """Verify that the 'logger' action runs without error."""
        # Also make this a bit faster :)
        with unittest.mock.patch.object(time, "sleep"):
            out = self.harness.run_action("logger")
        assert out.results is None
        assert out.logs == [
            "I'm counting to 10: 1",
            "I'm counting to 10: 2",
            "I'm counting to 10: 3",
            "I'm counting to 10: 4",
            "I'm counting to 10: 5",
            "I'm counting to 10: 6",
            "I'm counting to 10: 7",
            "I'm counting to 10: 8",
            "I'm counting to 10: 9",
            "I'm counting to 10: 10",
        ]
        assert not out.failure

    def test_bad(self):
        """Verify that the 'bad' action runs without error (but fails)."""
        out = self.harness.run_action("bad")
        assert out.results is None
        assert out.logs == []
        assert out.failure == "Sorry, I just couldn't manage it."

    def test_combo_fail(self):
        """Verify that the 'combo' action fails when instructed to do so."""
        out = self.harness.run_action("combo", {"should-fail": True})
        assert out.results is None
        assert out.logs == []
        assert out.failure

    def test_combo(self):
        """Verify that the 'combo' action runs without error."""
        my_fortunes = ["magazine", "500", "cookie"]
        with unittest.mock.patch.object(fortune, "get_random_fortune", side_effect=my_fortunes):
            out = self.harness.run_action("combo")
        assert out.results == {"fortunes-told": 3}
        assert out.logs == my_fortunes
        assert not out.failure
