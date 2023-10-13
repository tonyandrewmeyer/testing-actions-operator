# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

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
