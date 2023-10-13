# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

"""Test the charm using the Scenario framework."""

import fortune
import ops
import pytest
import scenario
from charm import TestingActionsCharm


@pytest.fixture()
def charm_meta():
    """Load the meta for the Charm."""
    with open("metadata.yaml") as meta:
        with open("actions.yaml") as actions:
            return ops.CharmMeta.from_yaml(meta, actions)


def test_simple():
    """Verify that the 'simple' action runs without error."""
    action = scenario.Action("simple")
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""


def test_input_default_value(caplog, charm_meta):
    """Verify that the 'input' action runs correctly (no arg is provided)."""
    # It doesn't seem like we can get the default parameters from scenario, at
    # least at the time we need to create the Action object.
    default_value = {
        key: details["default"] for key, details in charm_meta.actions["input"].parameters.items()
    }
    action = scenario.Action("input", params=default_value)
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""
    count = 0
    for record in caplog.records:
        if record.levelname == "DEBUG":
            # Ignore scenario's messages.
            continue
        count += 1
        assert record.levelname == "INFO"
        assert record.msg == f"The 'input' action says: {default_value['arg']}"
    assert count == 1


def test_input(caplog):
    """Verify that the 'input' action runs correctly (an arg is provided)."""
    response = "hello"
    action = scenario.Action("input", params={"arg": response})
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""
    count = 0
    for record in caplog.records:
        if record.levelname == "DEBUG":
            # Ignore scenario's messages.
            continue
        count += 1
        assert record.levelname == "INFO"
        assert record.msg == f"The 'input' action says: {response}"
    assert count == 1


def test_multi_input_default_value(caplog, charm_meta):
    """Verify that the 'multi-input' action runs correctly (no arg is provided)."""
    default_value = {
        key: details["default"]
        for key, details in charm_meta.actions["multi-input"].parameters.items()
    }
    action = scenario.Action("multi-input", params=default_value)
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""
    count = 0
    for record in caplog.records:
        if record.levelname == "DEBUG":
            # Ignore scenario's messages.
            continue
        count += 1
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {default_value['arg1']}"
    assert count == 1


def test_multi_input_arg1(caplog, charm_meta):
    """Verify that the 'multi-input' action runs correctly (arg1 is provided)."""
    default_value = {
        key: details["default"]
        for key, details in charm_meta.actions["multi-input"].parameters.items()
    }
    response = "hello"
    default_value["arg1"] = response
    action = scenario.Action("multi-input", params=default_value)
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""
    count = 0
    for record in caplog.records:
        if record.levelname == "DEBUG":
            # Ignore scenario's messages.
            continue
        count += 1
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {default_value['arg1']}"
    assert count == 1


def test_multi_input_arg2(caplog, charm_meta):
    """Verify that the 'multi-input' action runs correctly (arg2 is provided)."""
    default_value = {
        key: details["default"]
        for key, details in charm_meta.actions["multi-input"].parameters.items()
    }
    expected_count = 2
    default_value["arg2"] = expected_count
    action = scenario.Action("multi-input", params=default_value)
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""
    count = 0
    for record in caplog.records:
        if record.levelname == "DEBUG":
            # Ignore scenario's messages.
            continue
        count += 1
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {default_value['arg1']}"
    assert count == expected_count


def test_multi_input_arg1_and_arg2(caplog):
    """Verify that the 'multi-input' action runs correctly (arg1 and arg2 are provided)."""
    response = "hello"
    expected_count = 3
    params = {
        "arg1": response,
        "arg2": expected_count,
    }
    action = scenario.Action("multi-input", params=params)
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""
    count = 0
    for record in caplog.records:
        if record.levelname == "DEBUG":
            # Ignore scenario's messages.
            continue
        count += 1
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {params['arg1']}"
    assert count == expected_count


def test_output(monkeypatch):
    """Verify that the 'output' action runs correctly."""
    my_fortune = "favours the brave"
    monkeypatch.setattr(fortune, "get_random_fortune", lambda _: my_fortune)
    action = scenario.Action("output")
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results == {"fortune": my_fortune}
    assert out.logs == []
    assert out.failure == ""
