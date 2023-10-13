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


def test_input_default_value(harness, monkeypatch, caplog):
    """Verify that the 'input' action runs correctly (no arg is provided)."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "input")
    monkeypatch.setattr(
        harness.charm.framework.model._backend,
        "action_get",
        lambda: harness.charm.meta.actions["input"].parameters,
    )
    harness.charm.on.input_action.emit()
    default_value = harness.charm.meta.actions["input"].parameters["arg"]
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].msg == f"The 'input' action says: {default_value}"


def test_input(harness, monkeypatch, caplog):
    """Verify that the 'input' action runs correctly (an arg is provided)."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "input")
    response = "hello"
    params = {"arg": response}
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: params)
    harness.charm.on.input_action.emit()
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].msg == f"The 'input' action says: {response}"
