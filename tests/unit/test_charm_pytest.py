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


def test_simple(harness):
    """Verify that the 'simple' action runs without error."""
    out = harness.run_action("simple")
    assert out.results is None
    assert out.logs == []


def test_input_default_value(harness, caplog):
    """Verify that the 'input' action runs correctly (no arg is provided)."""
    out = harness.run_action("input")
    assert out.results is None
    assert out.logs == []
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    default_value = harness.charm.meta.actions["input"].parameters["arg"]
    assert caplog.records[0].msg == f"The 'input' action says: {default_value}"


def test_input(harness, caplog):
    """Verify that the 'input' action runs correctly (an arg is provided)."""
    response = "hello"
    out = harness.run_action("input", {"arg": response})
    assert out.results is None
    assert out.logs == []
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].msg == f"The 'input' action says: {response}"


def test_multi_input_default_value(harness, caplog):
    """Verify that the 'multi-input' action runs correctly (no arg is provided)."""
    out = harness.run_action("multi-input")
    assert out.results is None
    assert out.logs == []
    defaults = harness.charm.meta.actions["input"].parameters
    assert len(caplog.records) == defaults["int-arg"]["default"]
    for record in caplog.records:
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {defaults['str-arg']['default']}"


def test_multi_input_str_arg(harness, caplog):
    """Verify that the 'multi-input' action runs correctly (str_arg is provided)."""
    response = "hello"
    out = harness.run_action("multi-input", params={"str-arg": response})
    assert out.results is None
    assert out.logs == []
    defaults = harness.charm.meta.actions["input"].parameters
    assert len(caplog.records) == defaults["int-arg"]["default"]
    for record in caplog.record:
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {response}"


def test_multi_input_int_arg(harness, caplog):
    """Verify that the 'multi-input' action runs correctly (int-arg is provided)."""
    count = 2
    out = harness.run_action("multi-input", params={"int-arg": count})
    assert out.results is None
    assert out.logs == []
    defaults = harness.charm.meta.actions["input"].parameters
    assert len(caplog.records) == count
    for record in caplog.records:
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {defaults['str-arg']['default']}"


def test_multi_input_str_arg_and_int_arg(harness, caplog):
    """Verify that the 'multi-input' action runs correctly (str-arg and int-arg are provided)."""
    response = "hello"
    count = 3
    out = harness.run_action("multi-input", params={"str-arg": response, "int-arg": count})
    assert out.results is None
    assert out.logs == []
    assert len(caplog.records) == count
    for record in caplog.records:
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {response}"


def test_multi_input_all_args(harness, monkeypatch, caplog):
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
    out = harness.run_action("multi-input", params)
    assert out.results is None
    assert out.logs == []
    assert len(caplog.records) == count + 1
    for record in caplog.records[:-1]:
        assert record.levelname == "INFO"
        assert record.msg == f"The 'multi-input' action says: {response}"
    assert caplog.records[-1].levelname == "INFO"
    assert caplog.records[-1].msg == (
        f"The 'multi-input' action also says: {number}, {array}, and {obj}"
    )


def test_output(harness, monkeypatch):
    """Verify that the 'output' action runs correctly."""
    my_fortune = "favours the brave"
    monkeypatch.setattr(fortune, "get_random_fortune", lambda _: my_fortune)
    out = harness.run_action("output")
    assert out.results == {"fortune": my_fortune}
    assert out.logs == []


def test_logger(harness, monkeypatch):
    """Verify that the 'logger' action runs without error."""
    monkeypatch.setenv("JUJU_ACTION_NAME", "logger")
    collected_msgs = []

    def action_log(msg):
        collected_msgs.append(msg)

    monkeypatch.setattr(harness.charm.framework.model._backend, "action_get", lambda: None)
    monkeypatch.setattr(harness.charm.framework.model._backend, "action_log", action_log)
    # Also make this a bit faster :)
    monkeypatch.setattr(time, "sleep", lambda _: None)
    out = harness.run_action("logger")
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


def test_bad(harness):
    """Verify that the 'bad' action runs without error (but fails)."""
    exc = pytest.raises(ops.testing.ActionFailed, harness.run_action, "bad").value
    assert exc.output.results is None
    assert exc.logs == []
    assert exc.message == "Sorry, I just couldn't manage it."


def test_combo_fail(harness, monkeypatch):
    """Verify that the 'combo' action fails when instructed to do so."""
    pytest.raises(harness.run_action, "combo", **{"should-fail": True})


def test_combo(harness, monkeypatch):
    """Verify that the 'combo' action runs without error."""
    my_fortunes = ["magazine", "500", "cookie"]
    expected_fortunes = my_fortunes[:]
    monkeypatch.setattr(fortune, "get_random_fortune", lambda _: my_fortunes.pop(0))

    out = harness.run_action("combo")
    assert out.results == {"fortunes-told": 3}
    assert out.logs == expected_fortunes
