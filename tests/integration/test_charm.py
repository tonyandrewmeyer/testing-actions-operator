#!/usr/bin/env python3
# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.

import asyncio
import io
import json
import logging
import subprocess
from pathlib import Path

import pytest
import yaml
from pytest_operator.plugin import OpsTest, check_deps

logger = logging.getLogger(__name__)

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
APP_NAME = METADATA["name"]


@pytest.fixture()
async def multi_ops_test(request, tmp_path_factory):
    """Like pytest_operator.plugin.ops_test, but with different controllers."""
    check_deps("juju", "charmcraft")
    ops_test = OpsTest(request, tmp_path_factory)
    ops_test.controller_name = request.param
    await ops_test._setup_model()
    OpsTest._instance = ops_test
    yield ops_test
    OpsTest._instance = None
    await ops_test._cleanup_models()


def pytest_generate_tests(metafunc):
    """Duplicate all the tests to run on a localhost and microk8s cloud if available."""
    # Find a local machine and k8s controller, if possible. This assumes that
    # the Juju cli is available - doing this with multi_ops_test.juju is feasible but
    # requires setting up an OpsTest instance since we're too early for the
    # fixture to be ready, which is a lot of overhead for no real benefit.
    juju = subprocess.run(
        ["juju", "list-controllers", "--format=json"], check=True, capture_output=True
    )
    controllers = json.loads(juju.stdout)
    k8s_found = False
    machine_found = False
    run_under = []
    for controller_name, data in controllers["controllers"].items():
        if data["region"] != "localhost":
            continue
        if not k8s_found and data["cloud"] == "microk8s":
            k8s_found = True
            run_under.append(controller_name)
        elif not machine_found and data["cloud"] == "localhost":
            machine_found = True
            run_under.append(controller_name)
    if not run_under:
        # We didn't find any that matched, so just use the current controller.
        # (As is the default with pytest-operator).
        run_under.append(controllers["current-controller"])
    metafunc.parametrize("multi_ops_test", run_under, indirect=True)


@pytest.mark.abort_on_fail
async def test_deploy(multi_ops_test):
    """Build and deploy the charm.

    Assert on the unit status before any relations/configurations take place.
    """
    # Build the charm.
    # TODO: We could do this once and share the built charm across controllers.
    charm = await multi_ops_test.build_charm(".")

    # Deploy the charm and wait for active/idle status.
    await asyncio.gather(
        multi_ops_test.model.deploy(charm, resources={}, application_name=APP_NAME),
        multi_ops_test.model.wait_for_idle(
            apps=[APP_NAME], status="active", raise_on_blocked=True, timeout=180
        ),
    )


@pytest.fixture()
def app(multi_ops_test):
    return multi_ops_test.model.applications[APP_NAME]


@pytest.fixture()
def fortunes():
    with open("src/fortunes.txt") as content:
        return content.read()


async def test_simple(app, multi_ops_test):
    """Run the 'simple' action and ensure that the status stays active."""
    for unit in app.units:
        action = await unit.run_action("simple")
        action = await action.wait()
        assert action.status == "completed"


async def test_input(app, multi_ops_test):
    """Run the 'input' action and ensure the log entries are generated."""
    log = io.StringIO()
    modules = [f"unit.{unit.name}.juju-log" for unit in app.units]
    await multi_ops_test.model.debug_log(target=log, level="INFO", include_module=modules)
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


async def test_multi_input(app, multi_ops_test):
    """Run the 'multi-input' action and ensure the log entries are generated."""
    log = io.StringIO()
    modules = [f"unit.{unit.name}.juju-log" for unit in app.units]
    await multi_ops_test.model.debug_log(
        target=log, level="INFO", include_module=modules, limit=100
    )
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
