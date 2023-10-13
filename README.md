# testing-actions

A simple charm to exercise actions, and - more particularly - test actions.

## Installation

The charm can be built and installed in the usual way (see [Contributing](CONTRIBUTING.md) for
details). The charm supports both machine and K8s controllers.

## Available actions

The follow actions are available:

* `simple`: essentially a no-op
* `input`: optionally provide `arg` (a string) as input, and the content will be logged
    (e.g. visible in `juju debug-log`)
* `multi-input`: optionally provide `arg1` (a string), and `arg2` (a whole number) as input, and
    the content will be logged (e.g. visible in `juju debug-log`)
* `output`: returns a friendly message from the charm
* `logger`: takes a while, but tells you things while it's running
* `bad`: always fails
* `combo`: optionally provide `should-fail` (a Boolean) as input, and the action will fail or
    not as a result

## Other resources

- [OP-041 - Testing Actions with Harness](https://docs.google.com/document/d/1nxyiR7H7ZJZUIOfyIrEudmTg64jDJvPnPLCAeD1R7w0)
