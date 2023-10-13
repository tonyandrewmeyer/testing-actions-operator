# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

"""Test the charm using the Scenario framework."""

import scenario
from charm import TestingActionsCharm


def test_simple():
    """Verify that the 'simple' action runs without error."""
    # Define an action.
    action = scenario.Action("simple")
    ctx = scenario.Context(TestingActionsCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""
