"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system when the Abort command is executed in an EMPTY
observation state.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)
from tests.resources.test_support.constant_low import (
    DEVICE_OBS_STATE_EMPTY_INFO,
    TIMEOUT,
)

telescope_control = BaseTelescopeControl()


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_abort_command.feature",
    "TMC executes Abort Command in EMPTY obsState.",
)
def test_abort_command_not_allowed_empty():
    """BDD test scenario for verifying execution of the Abort
    command in EMPTY obsState in TMC."""


@given("a Subarray in EMPTY obsState")
def given_tmc(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Subarray in EMPTY obsState"""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    subarray_node_low.move_to_on()

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when("I Abort it")
def invoke_abort_command(subarray_node_low: SubarrayNodeWrapperLow):
    """Send a Abort command to the subarray."""
    pytest.unique_id, pytest.resultcode = subarray_node_low.execute_transition(
        "Abort"
    )


@then("TMC should reject the command with ResultCode.REJECTED")
def invalid_command_rejection(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """
    Verifies that the TMC rejects a command with ResultCode.REJECTED,
    and checks for a specific error message in the command result.
    """
    log_events({subarray_node_low.subarray_node: ["longRunningCommandResult"]})
    result = event_tracer.query_events(
        lambda e: e.has_device(subarray_node_low.subarray_node)
        and e.has_attribute("longRunningCommandResult")
        and e.current_value[0] == pytest.unique_id
        and json.loads(e.current_value[1])[0] == ResultCode.REJECTED
        and "Abort is not permitted" in json.loads(e.current_value[1])[1],
        timeout=TIMEOUT,
    )
    assert_that(result).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult ResultCode.REJECTED",
    ).is_length(1)


@then("the Subarray remains in obsState EMPTY")
def tmc_status():
    """
    Verifies that the Subarray remains in the observation state EMPTY.
    """
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    )
