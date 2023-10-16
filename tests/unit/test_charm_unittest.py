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
        self.assertIsNone(out.results)
        self.assertEqual(out.logs, [])
        self.assertTrue(out.success)

    def test_input_default_value(self):
        """Verify that the 'input' action runs correctly (no arg is provided)."""
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("input")
        self.assertIsNone(out.results)
        self.assertEqual(out.logs, [])
        self.assertTrue(out.success)
        default_value = self.harness.charm.meta.actions["input"].parameters["arg"]
        self.assertEqual(cm.output, [f"INFO:charm:The 'input' action says: {default_value}"])

    def test_input(self):
        """Verify that the 'input' action runs correctly (an arg is provided)."""
        response = "hello"
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("input", {"arg": response})
        self.assertIsNone(out.results)
        self.assertEqual(out.logs, [])
        self.assertTrue(out.success)
        self.assertEqual(cm.output, [f"INFO:charm:The 'input' action says: {response}"])

    def test_multi_input_default_value(self):
        """Verify that the 'multi-input' action runs correctly (no arg is provided)."""
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("multi-input")
        self.assertIsNone(out.results)
        self.assertEqual(out.logs, [])
        self.assertTrue(out.success)
        defaults = self.harness.charm.meta.actions["input"].parameters
        self.assertEqual(
            cm.output, [f"INFO:charm:The 'multi-input' action says: {defaults['str-arg']['default']}"]
        )

    def test_multi_input_str_arg(self):
        """Verify that the 'multi-input' action runs correctly (str_arg is provided)."""
        response = "hello"
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("multi-input", params={"str-arg": response})
        self.assertIsNone(out.results)
        self.assertEqual(out.logs, [])
        self.assertTrue(out.success)
        self.assertEqual(cm.output, [f"INFO:charm:The 'multi-input' action says: {response}"])

    def test_multi_input_int_arg(self):
        """Verify that the 'multi-input' action runs correctly (int_arg is provided)."""
        count = 2
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("multi-input", params={"int_arg": count})
        self.assertIsNone(out.results)
        self.assertEqual(out.logs, [])
        self.assertTrue(out.success)
        defaults = self.harness.charm.meta.actions["input"].parameters
        self.assertEqual(
            cm.output,
            [f"INFO:charm:The 'multi-input' action says: {defaults['str-arg']['default']}"] * count,
        )

    def test_multi_input_str_arg_and_int_arg(self):
        """Verify that the 'multi-input' action runs correctly (str_arg and int_arg are provided)."""
        response = "hello"
        count = 3
        with self.assertLogs(level="INFO") as cm:
            out = self.harness.run_action("multi-input", params={"str-arg": response, "int-arg": count})
        self.assertIsNone(out.results)
        self.assertEqual(out.logs, [])
        self.assertTrue(out.success)
        self.assertEqual(
            cm.output, [f"INFO:charm:The 'multi-input' action says: {response}"] * count
        )

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "multi-input"})
    def test_multi_input_all_args(self):
        """Verify that the 'multi-input' action runs correctly (all args are provided)."""
        response = "hello"
        count = 3
        extra_log = True
        number = 28.8
        obj = {"foo": "bar"}
        array = ["jan", "apr", "jul", "oct"]
        params = {
            "str-arg": response,
            "int-arg": count,
            "bool-arg": extra_log,
            "obj-arg": obj,
            "array-arg": array,
            "num-arg": number,
        }
        with self.assertLogs(level="INFO") as cm:
            self.harness.run_action("multi-input", params)
        expected_output = [f"INFO:charm:The 'multi-input' action says: {response}"] * count
        expected_output.append(
            f"INFO:charm:The 'multi-input' action also says: {number}, {array}, and {obj}"
        )
        self.assertEqual(cm.output, expected_output)

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "output"})
    def test_output(self):
        """Verify that the 'output' action runs correctly."""
        my_fortune = "favours the brave"
        with unittest.mock.patch.object(fortune, "get_random_fortune", return_value=my_fortune):
            out = self.harness.run_action("output")
        self.assertEqual(out.results, {"fortune": my_fortune})
        self.assertEqual(out.logs, [])
        self.assertTrue(out.success)

    def test_logger(self):
        """Verify that the 'logger' action runs without error."""
        # Also make this a bit faster :)
        with unittest.mock.patch.object(time, "sleep"):
            out = self.harness.run_action("logger")
        self.assertIsNone(out.results)
        self.assertEqual(
            out.logs,
            [
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
            ],
        )
        self.assertTrue(out.success)

    def test_bad(self):
        """Verify that the 'bad' action runs without error (but fails)."""
        out = self.harness.run_action("bad")
        self.assertIsNone(out.results)
        self.assertEqual(out.logs, [])
        self.assertFalse(out.success)
        self.assertEqual(out.failure, "Sorry, I just couldn't manage it.")

    def test_combo_fail(self):
        """Verify that the 'combo' action fails when instructed to do so."""
        out = self.harness.run_action("combo", {"should-fail": True})
        self.assertIsNone(out.results)
        self.assertEqual(out.logs, [])
        self.assertFalse(out.success)

    def test_combo(self):
        """Verify that the 'combo' action runs without error."""
        my_fortunes = ["magazine", "500", "cookie"]
        with unittest.mock.patch.object(fortune, "get_random_fortune", side_effect=my_fortunes):
            out = self.harness.run_action("combo")
        self.assertEqual(out.results, {"fortunes-told": 3})
        self.assertEqual(out.logs, my_fortunes)
        self.assertTrue(out.success)
