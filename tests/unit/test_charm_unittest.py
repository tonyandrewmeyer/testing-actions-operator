# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

"""Test the charm using Harness with unittest."""

import os
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

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "simple"})
    def test_simple(self):
        """Verify that the 'simple' action runs without error."""
        with unittest.mock.patch.object(self.harness.charm.framework.model._backend, "action_get"):
            self.harness.charm.on.simple_action.emit()

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "input"})
    def test_input_default_value(self):
        """Verify that the 'input' action runs correctly (no arg is provided)."""
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            unittest.mock.MagicMock(
                return_value=self.harness.charm.meta.actions["input"].parameters
            ),
        ):
            with self.assertLogs(level="INFO") as cm:
                self.harness.charm.on.input_action.emit()
        default_value = self.harness.charm.meta.actions["input"].parameters["arg"]
        self.assertEqual(cm.output, [f"INFO:charm:The 'input' action says: {default_value}"])

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "input"})
    def test_input(self):
        """Verify that the 'input' action runs correctly (an arg is provided)."""
        response = "hello"
        params = {"arg": response}
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            unittest.mock.MagicMock(return_value=params),
        ):
            with self.assertLogs(level="INFO") as cm:
                self.harness.charm.on.input_action.emit()
        self.assertEqual(cm.output, [f"INFO:charm:The 'input' action says: {response}"])

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "multi-input"})
    def test_multi_input_default_value(self):
        """Verify that the 'multi-input' action runs correctly (no arg is provided)."""
        params = {
            key: details["default"]
            for key, details in self.harness.charm.meta.actions["multi-input"].parameters.items()
        }
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            unittest.mock.MagicMock(return_value=params),
        ):
            with self.assertLogs(level="INFO") as cm:
                self.harness.charm.on.multi_input_action.emit()
        self.assertEqual(
            cm.output, [f"INFO:charm:The 'multi-input' action says: {params['arg1']}"]
        )

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "multi-input"})
    def test_multi_input_arg1(self):
        """Verify that the 'multi-input' action runs correctly (arg1 is provided)."""
        params = {
            key: details["default"]
            for key, details in self.harness.charm.meta.actions["multi-input"].parameters.items()
        }
        response = "hello"
        params["arg1"] = response
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            unittest.mock.MagicMock(return_value=params),
        ):
            with self.assertLogs(level="INFO") as cm:
                self.harness.charm.on.multi_input_action.emit()
        self.assertEqual(cm.output, [f"INFO:charm:The 'multi-input' action says: {response}"])

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "multi-input"})
    def test_multi_input_arg2(self):
        """Verify that the 'multi-input' action runs correctly (arg2 is provided)."""
        params = {
            key: details["default"]
            for key, details in self.harness.charm.meta.actions["multi-input"].parameters.items()
        }
        count = 2
        params["arg2"] = count
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            unittest.mock.MagicMock(return_value=params),
        ):
            with self.assertLogs(level="INFO") as cm:
                self.harness.charm.on.multi_input_action.emit()
        self.assertEqual(
            cm.output, [f"INFO:charm:The 'multi-input' action says: {params['arg1']}"] * count
        )

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "multi-input"})
    def test_multi_input_arg1_and_arg2(self):
        """Verify that the 'multi-input' action runs correctly (arg1 and arg2 are provided)."""
        response = "hello"
        count = 3
        params = {"arg1": response, "arg2": count}
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            unittest.mock.MagicMock(return_value=params),
        ):
            with self.assertLogs(level="INFO") as cm:
                self.harness.charm.on.multi_input_action.emit()
        self.assertEqual(
            cm.output, [f"INFO:charm:The 'multi-input' action says: {response}"] * count
        )

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "output"})
    def test_output(self):
        """Verify that the 'output' action runs correctly."""
        my_fortune = "favours the brave"
        with unittest.mock.patch.object(self.harness.charm.framework.model._backend, "action_get"):
            with unittest.mock.patch.object(
                fortune, "get_random_fortune", return_value=my_fortune
            ):
                with unittest.mock.patch.object(
                    self.harness.charm.framework.model._backend, "action_set"
                ) as mock_set:
                    self.harness.charm.on.output_action.emit()
                    mock_set.assert_called_once_with({"fortune": my_fortune})

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "logger"})
    def test_logger(self):
        """Verify that the 'simple' action runs without error."""
        with unittest.mock.patch.object(self.harness.charm.framework.model._backend, "action_get"):
            with unittest.mock.patch.object(
                self.harness.charm.framework.model._backend, "action_log"
            ) as mock_log:
                # Also make this a bit faster :)
                with unittest.mock.patch.object(time, "sleep"):
                    self.harness.charm.on.logger_action.emit()
                    mock_log.assert_has_calls(
                        [
                            unittest.mock.call("I'm counting to 10: 1"),
                            unittest.mock.call("I'm counting to 10: 2"),
                            unittest.mock.call("I'm counting to 10: 3"),
                            unittest.mock.call("I'm counting to 10: 4"),
                            unittest.mock.call("I'm counting to 10: 5"),
                            unittest.mock.call("I'm counting to 10: 6"),
                            unittest.mock.call("I'm counting to 10: 7"),
                            unittest.mock.call("I'm counting to 10: 8"),
                            unittest.mock.call("I'm counting to 10: 9"),
                            unittest.mock.call("I'm counting to 10: 10"),
                        ]
                    )

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "bad"})
    def test_bad(self):
        """Verify that the 'bad' action runs without error (but fails)."""
        with unittest.mock.patch.object(self.harness.charm.framework.model._backend, "action_get"):
            with unittest.mock.patch.object(
                self.harness.charm.framework.model._backend, "action_fail"
            ) as mock_fail:
                self.harness.charm.on.bad_action.emit()
                mock_fail.assert_called_once()
