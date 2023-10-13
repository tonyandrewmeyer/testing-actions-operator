# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

"""Test the charm using Harness with pytest."""

import ops
import ops.testing
import pytest
from charm import TestingActionsCharm


@pytest.fixture()
def harness():
    """Create a testing harness to use for the tests.

    ``begin()`` has already been called for you.
    """
    harness = ops.testing.Harness(TestingActionsCharm)
    harness.begin()
    yield harness
    harness.cleanup()


def test_simple(harness, monkeypatch):
    """Verify that the 'simple' action runs without error."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "simple")
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: None)
    harness.charm.on.simple_action.emit()
