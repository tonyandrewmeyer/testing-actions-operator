#!/usr/bin/env python3
# Copyright 2023 Tony Meyer
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Actions Demonstration Charm.

A simple charm that has some demo actions, designed to explain and explore how
testing those actions should optimally be done.
"""

import logging
import os
import time

import fortune
import ops
import requests

logger = logging.getLogger(__name__)

FORTUNE_SOURCE = "https://raw.githubusercontent.com/bmc/fortunes/master/fortunes"


class ActionsTestingCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, framework: ops.Framework):
        """Set up the charm."""
        super().__init__(framework)
        self._fortune_file = "fortunes.txt"
        self.framework.observe(self.on.install, self._prepare_something_to_say)
        self.framework.observe(self.on.upgrade_charm, self._prepare_something_to_say)
        self.framework.observe(self.on.simple_action, self._on_simple_action)
        self.framework.observe(self.on.input_action, self._on_input_action)
        self.framework.observe(self.on.multi_input_action, self._on_multi_input_action)
        self.framework.observe(self.on.output_action, self._on_output_action)
        self.framework.observe(self.on.logger_action, self._on_logger_action)
        self.framework.observe(self.on.bad_action, self._on_bad_action)
        self.framework.observe(self.on.combo_action, self._on_combo_action)

    def _prepare_something_to_say(self, event: ops.EventBase):
        """Get ready to provide something interesting to the user."""
        # We could also check if the file seems old, but this will suffice for now.
        if not os.path.exists(self._fortune_file):
            response = requests.get(FORTUNE_SOURCE, timeout=60)
            response.raise_for_status()
            with open(self._fortune_file, "w") as fout:
                fout.write(response.text)
        self.unit.status = ops.ActiveStatus()  # noqa: F841

    def _on_simple_action(self, event: ops.ActionEvent):
        """Do nothing, just log that we did that."""
        logger.info("Hello from the 'simple' action!")

    def _on_input_action(self, event: ops.ActionEvent):
        """Log whatever input we were given."""
        logger.info(f"The 'input' action says: {event.params['arg']}")

    def _on_multi_input_action(self, event: ops.ActionEvent):
        """Log whatever input we were given, as many times as we are told."""
        for _ in range(event.params["arg2"]):
            logger.info(f"The 'multi-input' action says: {event.params['arg1']}")

    def _on_output_action(self, event: ops.ActionEvent):
        """Say something back to the user."""
        event.set_results({"fortune": fortune.get_random_fortune(self._fortune_file)})

    def _on_logger_action(self, event: ops.ActionEvent):
        """Do nothing, but talk to the user while we do it."""
        end = 10
        for i in range(end):
            event.log(f"I'm counting to {end}: {i + 1}")
            time.sleep(1)

    def _on_bad_action(self, event: ops.ActionEvent):
        """Fail, every time, no matter how hard you try."""
        event.fail("Sorry, I just couldn't manage it.")

    def _on_combo_action(self, event: ops.ActionEvent):
        """Tell the user a few fortunes, unless they want us to fail."""
        if event.params["should-fail"]:
            event.fail("As you requested!")
            return
        count = 3
        for _ in range(count):
            event.log(fortune.get_random_fortune(self._fortune_file))
        event.set_results({"fortunes-told": count})


if __name__ == "__main__":  # pragma: nocover
    ops.main(ActionsTestingCharm)  # type: ignore
