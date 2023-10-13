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
