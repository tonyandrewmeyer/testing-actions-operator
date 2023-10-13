# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

"""Test the charm using the Scenario framework."""

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
    for record in caplog.records:
        if record.levelname == "DEBUG":
            # Ignore scenario's messages.
            continue
        assert record.levelname == "INFO"
        assert record.msg == f"The 'input' action says: {default_value['arg']}"


def test_input(caplog):
    """Verify that the 'input' action runs correctly (an arg is provided)."""
    response = "hello"
    action = scenario.Action("input", params={"arg": response})
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""
    for record in caplog.records:
        if record.levelname == "DEBUG":
            # Ignore scenario's messages.
            continue
        assert record.levelname == "INFO"
        assert record.msg == f"The 'input' action says: {response}"
