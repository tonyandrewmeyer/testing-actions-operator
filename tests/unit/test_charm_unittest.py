# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

"""Test the charm using Harness with unittest."""

import os
import unittest
import unittest.mock

import ops
import ops.testing
from charm import TestingActionsCharm


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = ops.testing.Harness(TestingActionsCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "simple"})
    def test_simple(self):
        """Verify that the 'simple' action runs without error."""
        self.harness.charm.framework.model._backend.action_get = unittest.mock.MagicMock()
        self.harness.charm.on.simple_action.emit()

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "input"})
    def test_input_default_value(self):
        """Verify that the 'input' action runs correctly (no arg is provided)."""
        self.harness.charm.framework.model._backend.action_get = unittest.mock.MagicMock(
            return_value=self.harness.charm.meta.actions["input"].parameters
        )
        with self.assertLogs(level="INFO") as cm:
            self.harness.charm.on.input_action.emit()
        default_value = self.harness.charm.meta.actions["input"].parameters["arg"]
        self.assertEqual(cm.output, [f"INFO:charm:The 'input' action says: {default_value}"])

    @unittest.mock.patch.dict(os.environ, {"JUJU_ACTION_NAME": "input"})
    def test_input(self):
        """Verify that the 'input' action runs correctly (an arg is provided)."""
        response = "hello"
        params = {"arg": response}
        self.harness.charm.framework.model._backend.action_get = unittest.mock.MagicMock(
            return_value=params
        )
        with self.assertLogs(level="INFO") as cm:
            self.harness.charm.on.input_action.emit()
        self.assertEqual(cm.output, [f"INFO:charm:The 'input' action says: {response}"])
