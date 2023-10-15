#!/usr/bin/env python3
# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.

import asyncio
import io
import logging
from pathlib import Path

import pytest
import yaml

logger = logging.getLogger(__name__)

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
APP_NAME = METADATA["name"]


@pytest.mark.abort_on_fail
async def test_deploy(ops_test):
    """Build and deploy the charm.

    Assert on the unit status before any relations/configurations take place.
    """
    # Build the charm.
    charm = await ops_test.build_charm(".")

    # Deploy the charm and wait for active/idle status.
    await asyncio.gather(
        ops_test.model.deploy(charm, resources={}, application_name=APP_NAME),
        ops_test.model.wait_for_idle(
            apps=[APP_NAME], status="active", raise_on_blocked=True, timeout=180
        ),
    )


@pytest.fixture()
def app(ops_test):
    return ops_test.model.applications[APP_NAME]


@pytest.fixture()
def fortunes():
    with open("src/fortunes.txt") as content:
        return content.read()


async def test_simple(app, ops_test):
    """Run the 'simple' action and ensure that the status stays active."""
    for unit in app.units:
        action = await unit.run_action("simple")
        action = await action.wait()
        assert action.status == "completed"


async def test_input(app, ops_test):
    """Run the 'input' action and ensure the log entries are generated."""
    log = io.StringIO()
    modules = [f"unit.{unit.name}.juju-log" for unit in app.units]
    await ops_test.model.debug_log(target=log, level="INFO", include_module=modules)
    arg = "hello"
    for unit in app.units:
        action = await unit.run_action("input", arg=arg)
        action = await action.wait()
        assert action.status == "completed"
    matches = 0
    for line in log.getvalue().splitlines():
        if f"The 'input' action says: {arg}" in line:
            matches += 1
    assert matches == len(app.units)


@pytest.mark.skip(reason="Getting the debug log output isn't working, even though test_input does")
async def test_multi_input(app, ops_test):
    """Run the 'multi-input' action and ensure the log entries are generated."""
    log = io.StringIO()
    modules = [f"unit.{unit.name}.juju-log" for unit in app.units]
    await ops_test.model.debug_log(target=log, level="INFO", include_module=modules)
    arg = "world"
    count = 2
    for unit in app.units:
        action = await unit.run_action("multi-input", arg1=arg, arg2=count)
        action = await action.wait()
        assert action.status == "completed"
    matches = 0
    for line in log.getvalue().splitlines():
        if f"The 'multi-input' action says: {arg}" in line:
            matches += 1
    assert matches == count * len(app.units), log.getvalue()


async def test_output(app, fortunes):
    """Run the 'output' action and ensure the correct output is returned."""
    for unit in app.units:
        action = await unit.run_action("output")
        action = await action.wait()
        assert action.results["return-code"] == 0
        assert action.results["fortune"] in fortunes
        assert action.status == "completed"


async def test_logger(app):
    """Run the 'logger' action and ensure that the appropriate updates are received."""
    for unit in app.units:
        action = await unit.run_action("logger")
        # Annoyingly, this will take 10s to run.
        # TODO: check that we got the log messages.
        # It doesn't seem possible to get the action logs in pylibjuju, at least
        # without significant work.
        action = await action.wait()
        assert action.status == "completed"


async def test_bad(app):
    """Run the 'bad' action and ensure that the resulting task status is failed."""
    for unit in app.units:
        action = await unit.run_action("bad")
        action = await action.wait()
        assert action.status == "failed"


async def test_combo_failed(app):
    """Run the 'combo' action with should-fail and ensure that the task status is failed."""
    kwargs = {"should-fail": True}  # the action is not a valid Python name.
    for unit in app.units:
        action = await unit.run_action("combo", **kwargs)
        action = await action.wait()
        assert action.status == "failed"


async def test_combo(app, fortunes):
    """Run the 'combo' action ensure that the correct output is returned."""
    for unit in app.units:
        action = await unit.run_action("combo")
        action = await action.wait()
        # TODO: check that the fortunes are sent as logs.
        # It doesn't seem possible to get the action logs in pylibjuju, at least
        # without significant work.
        assert action.results["return-code"] == 0
        assert action.results["fortunes-told"] == "3"
        assert action.status == "completed"
