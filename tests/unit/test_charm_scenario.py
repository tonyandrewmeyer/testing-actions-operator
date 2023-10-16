# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

"""Test the charm using the Scenario framework."""

import time

import fortune
import ops
import pytest
import scenario
from charm import ActionsTestingCharm


@pytest.fixture()
def charm_meta():
    """Load the meta for the Charm."""
    with open("metadata.yaml") as meta:
        with open("actions.yaml") as actions:
            return ops.CharmMeta.from_yaml(meta, actions)


def test_simple():
    """Verify that the 'simple' action runs without error."""
    ctx = scenario.Context(ActionsTestingCharm)
    out = ctx.run_action("simple", scenario.State())
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
    ctx = scenario.Context(ActionsTestingCharm)
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
    ctx = scenario.Context(ActionsTestingCharm)
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


@pytest.mark.skip(reason="scenario does not support integer params")
def test_multi_input_default_value(caplog, charm_meta):
    """Verify that the 'multi-input' action runs correctly (no arg is provided)."""
    default_value = {
        key: details["default"]
        for key, details in charm_meta.actions["multi-input"].parameters.items()
    }
    action = scenario.Action("multi-input", params=default_value)
    ctx = scenario.Context(ActionsTestingCharm)
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
        assert record.msg == f"The 'multi-input' action says: {default_value['str-arg']}"
    assert count == 1


# See https://github.com/canonical/ops-scenario/issues/66
@pytest.mark.skip(reason="scenario does not support integer params")
def test_multi_input_str_arg(caplog, charm_meta):
    """Verify that the 'multi-input' action runs correctly (str-arg is provided)."""
    default_value = {
        key: details["default"]
        for key, details in charm_meta.actions["multi-input"].parameters.items()
    }
    response = "hello"
    default_value["str-arg"] = response
    action = scenario.Action("multi-input", params=default_value)
    ctx = scenario.Context(ActionsTestingCharm)
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
        assert record.msg == f"The 'multi-input' action says: {default_value['str-arg']}"
    assert count == 1


# See https://github.com/canonical/ops-scenario/issues/66
@pytest.mark.skip(reason="scenario does not support integer params")
def test_multi_input_int_arg(caplog, charm_meta):
    """Verify that the 'multi-input' action runs correctly (int_arg is provided)."""
    default_value = {
        key: details["default"]
        for key, details in charm_meta.actions["multi-input"].parameters.items()
    }
    expected_count = 2
    default_value["int-arg"] = expected_count
    action = scenario.Action("multi-input", params=default_value)
    ctx = scenario.Context(ActionsTestingCharm)
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
        assert record.msg == f"The 'multi-input' action says: {default_value['str-arg']}"
    assert count == expected_count


# See https://github.com/canonical/ops-scenario/issues/66
@pytest.mark.skip(reason="scenario does not support integer params")
def test_multi_input_str_arg_and_int_arg(caplog):
    """Verify that the 'multi-input' action runs correctly (str-arg and int_arg are provided)."""
    response = "hello"
    expected_count = 3
    params = {
        "str-arg": response,
        "int-arg": expected_count,
    }
    action = scenario.Action("multi-input", params=params)
    ctx = scenario.Context(ActionsTestingCharm)
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
        assert record.msg == f"The 'multi-input' action says: {params['str-arg']}"
    assert count == expected_count


# See https://github.com/canonical/ops-scenario/issues/66
@pytest.mark.skip(reason="scenario does not support integer params")
def test_multi_input_all_args(caplog):
    """Verify that the 'multi-input' action runs correctly (all args are provided)."""
    response = "hello"
    expected_count = 3
    extra_log = True
    number = 28.8
    obj = {"foo": "bar"}
    array = ["jan", "apr", "jul", "oct"]
    params = {
        "str-arg": response,
        "int-arg": expected_count,
        "bool-arg": extra_log,
        "obj-arg": obj,
        "array-arg": array,
        "num-arg": number,
    }
    action = scenario.Action("multi-input", params=params)
    ctx = scenario.Context(ActionsTestingCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure == ""
    count = 0
    for record in caplog.records[:-1]:
        if record.levelname == "DEBUG":
            # Ignore scenario's messages.
            continue
        count += 1
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {params['str-arg']}"
    assert count == expected_count + 1
    assert caplog.records[-1].levelname == "INFO"
    assert caplog.records[-1].msg == (
        f"The 'multi-input' action also says: {number}, {array}, and {obj}"
    )


def test_output(monkeypatch):
    """Verify that the 'output' action runs correctly."""
    my_fortune = "favours the brave"
    monkeypatch.setattr(fortune, "get_random_fortune", lambda _: my_fortune)
    ctx = scenario.Context(ActionsTestingCharm)
    out = ctx.run_action("output", scenario.State())
    assert out.results == {"fortune": my_fortune}
    assert out.logs == []
    assert out.failure == ""


def test_logger(monkeypatch):
    """Verify that the 'logger' action runs without error."""
    # Also make this a bit faster :)
    monkeypatch.setattr(time, "sleep", lambda _: None)
    ctx = scenario.Context(ActionsTestingCharm)
    out = ctx.run_action("logger", scenario.State())
    assert out.results is None
    assert out.logs == [
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
    assert out.failure == ""


def test_bad():
    """Verify that the 'bad' action runs without error (but fails)."""
    ctx = scenario.Context(ActionsTestingCharm)
    out = ctx.run_action("bad", scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure


def test_combo_fail():
    """Verify that the 'combo' action fails when instructed to do so."""
    action = scenario.Action("combo", params={"should-fail": True})
    ctx = scenario.Context(ActionsTestingCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results is None
    assert out.logs == []
    assert out.failure


def test_combo(monkeypatch):
    """Verify that the 'combo' action runs without error."""
    my_fortunes = ["magazine", "500", "cookie"]
    expected_fortunes = my_fortunes[:]
    monkeypatch.setattr(fortune, "get_random_fortune", lambda _: my_fortunes.pop(0))

    action = scenario.Action("combo", params={"should-fail": False})
    ctx = scenario.Context(ActionsTestingCharm)
    out = ctx.run_action(action, scenario.State())
    assert out.results == {"fortunes-told": 3}
    assert out.logs == expected_fortunes
    assert out.failure == ""
