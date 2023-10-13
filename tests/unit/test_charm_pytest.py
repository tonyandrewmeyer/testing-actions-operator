# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

"""Test the charm using Harness with pytest."""

import time

import fortune
import ops
import ops.testing
import pytest
from charm import ActionsTestingCharm


@pytest.fixture()
def harness():
    """Create a testing harness to use for the tests.

    ``begin()`` has already been called for you.
    """
    harness = ops.testing.Harness(ActionsTestingCharm)
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


def test_multi_input_default_value(harness, monkeypatch, caplog):
    """Verify that the 'multi-input' action runs correctly (no arg is provided)."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "multi-input")
    params = {
        key: details["default"]
        for key, details in harness.charm.meta.actions["multi-input"].parameters.items()
    }
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: params)
    harness.charm.on.multi_input_action.emit()
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].msg == f"The 'multi-input' action says: {params['arg1']}"


def test_multi_input_arg1(harness, monkeypatch, caplog):
    """Verify that the 'multi-input' action runs correctly (arg1 is provided)."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "multi-input")
    params = {
        key: details["default"]
        for key, details in harness.charm.meta.actions["multi-input"].parameters.items()
    }
    response = "hello"
    params["arg1"] = response
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: params)
    harness.charm.on.multi_input_action.emit()
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].msg == f"The 'multi-input' action says: {response}"


def test_multi_input_arg2(harness, monkeypatch, caplog):
    """Verify that the 'multi-input' action runs correctly (arg2 is provided)."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "multi-input")
    params = {
        key: details["default"]
        for key, details in harness.charm.meta.actions["multi-input"].parameters.items()
    }
    count = 2
    params["arg2"] = count
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: params)
    harness.charm.on.multi_input_action.emit()
    assert len(caplog.records) == count
    for record in caplog.records:
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {params['arg1']}"


def test_multi_input_arg1_and_arg2(harness, monkeypatch, caplog):
    """Verify that the 'multi-input' action runs correctly (arg1 and arg2 are provided)."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "multi-input")
    response = "hello"
    count = 3
    params = {"arg1": response, "arg2": count}
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: params)
    harness.charm.on.multi_input_action.emit()
    assert len(caplog.records) == count
    for record in caplog.records:
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {response}"


def test_output(harness, monkeypatch):
    """Verify that the 'output' action runs correctly."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "output")
    my_fortune = "favours the brave"
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: None)
    monkeypatch.setattr(fortune, "get_random_fortune", lambda _: my_fortune)
    collected_results = []

    def action_set(results):
        collected_results.append(results)

    monkeypatch.setattr(harness.charm.framework.model._backend, "action_set", action_set)
    harness.charm.on.output_action.emit()
    assert collected_results == [{"fortune": my_fortune}]


def test_logger(harness, monkeypatch):
    """Verify that the 'simple' action runs without error."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "logger")
    collected_msgs = []

    def action_log(msg):
        collected_msgs.append(msg)

    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: None)
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_log", action_log)
    # Also make this a bit faster :)
    monkeypatch.setattr(time, "sleep", lambda _: None)
    harness.charm.on.logger_action.emit()
    assert collected_msgs == [
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


def test_bad(harness, monkeypatch):
    """Verify that the 'bad' action runs without error (but fails)."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "bad")
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: None)
    called = False

    def action_fail(msg):
        nonlocal called
        called = True

    monkeypatch.setattr(harness.charm.framework.model._backend, "action_fail", action_fail)
    harness.charm.on.bad_action.emit()
    assert called
