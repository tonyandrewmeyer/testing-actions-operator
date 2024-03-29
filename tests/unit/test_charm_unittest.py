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
            cm.output, [f"INFO:charm:The 'multi-input' action says: {params['str-arg']}"]
        )

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "multi-input"})
    def test_multi_input_str_arg(self):
        """Verify that the 'multi-input' action runs correctly (str-arg is provided)."""
        params = {
            key: details["default"]
            for key, details in self.harness.charm.meta.actions["multi-input"].parameters.items()
        }
        response = "hello"
        params["str-arg"] = response
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            unittest.mock.MagicMock(return_value=params),
        ):
            with self.assertLogs(level="INFO") as cm:
                self.harness.charm.on.multi_input_action.emit()
        self.assertEqual(cm.output, [f"INFO:charm:The 'multi-input' action says: {response}"])

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "multi-input"})
    def test_multi_input_int_arg(self):
        """Verify that the 'multi-input' action runs correctly (int-arg is provided)."""
        params = {
            key: details["default"]
            for key, details in self.harness.charm.meta.actions["multi-input"].parameters.items()
        }
        count = 2
        params["int-arg"] = count
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            unittest.mock.MagicMock(return_value=params),
        ):
            with self.assertLogs(level="INFO") as cm:
                self.harness.charm.on.multi_input_action.emit()
        self.assertEqual(
            cm.output, [f"INFO:charm:The 'multi-input' action says: {params['str-arg']}"] * count
        )

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "multi-input"})
    def test_multi_input_str_arg_and_int_arg(self):
        """Verify that the 'multi-input' action runs correctly (str-arg and int-arg are provided)."""
        params = {
            key: details["default"]
            for key, details in self.harness.charm.meta.actions["multi-input"].parameters.items()
        }
        response = "hello"
        count = 3
        params["str-arg"] = response
        params["int-arg"] = count
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
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            unittest.mock.MagicMock(return_value=params),
        ):
            with self.assertLogs(level="INFO") as cm:
                self.harness.charm.on.multi_input_action.emit()
        expected_output = [f"INFO:charm:The 'multi-input' action says: {response}"] * count
        expected_output.append(
            f"INFO:charm:The 'multi-input' action also says: {number}, {array}, and {obj}"
        )
        self.assertEqual(cm.output, expected_output)

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
        """Verify that the 'logger' action runs without error."""
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

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "combo"})
    def test_combo_fail(self):
        """Verify that the 'combo' action fails when instructed to do so."""
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            return_value={"should-fail": True},
        ):
            with unittest.mock.patch.object(
                self.harness.charm.framework.model._backend, "action_fail"
            ) as mock_fail:
                self.harness.charm.on.combo_action.emit()
                mock_fail.assert_called_once()

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "combo"})
    def test_combo(self):
        """Verify that the 'combo' action runs without error."""
        my_fortunes = ["magazine", "500", "cookie"]
        with unittest.mock.patch.object(
            self.harness.charm.framework.model._backend,
            "action_get",
            return_value={"should-fail": False},
        ):
            with unittest.mock.patch.object(
                self.harness.charm.framework.model._backend, "action_log"
            ) as mock_log:
                with unittest.mock.patch.object(
                    fortune, "get_random_fortune", side_effect=my_fortunes
                ):
                    with unittest.mock.patch.object(
                        self.harness.charm.framework.model._backend, "action_set"
                    ) as mock_set:
                        self.harness.charm.on.combo_action.emit()
                        mock_log.assert_has_calls([unittest.mock.call(f) for f in my_fortunes])
                        mock_set.assert_called_once_with({"fortunes-told": 3})
