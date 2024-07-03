"""
This module defines a Pytest BDD test scenario for the successful execution of
Abort command of a Low Telescope Subarray in the Telescope Monitoring
and Control (TMC) system.
"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_harness.constant import TIMEOUT
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    set_subarray_to_given_obs_state,
)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_abort_command.feature",
    "TMC validates Abort Command",
)
def test_tmc_abort_command():
    """BDD test scenario for verifying successful execution of
    the Abort command in a TMC."""


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_abort_command.feature",
    "TMC validates Abort Command in intermediate obsState",
)
def test_tmc_abort_command_in_intermediate_obs_state():
    """BDD test scenario for verifying successful execution of
    the Abort command in a TMC for intermediate obsStates."""


@given(parsers.parse("a Subarray in {obs_state} obsState"))
def given_tmc(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    obs_state: str,
):
    """Set up a TMC and ensure it is in the given ObsState."""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    log_events({subarray_node_low.subarray_node: "obsState"})
    subarray_node_low.move_to_on()
    subarray_node_low.force_change_of_obs_state(obs_state)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        f'"a Subarray in {obs_state} obsState"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        f"is expected to be in {obs_state} obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState[obs_state],
    )


@given(parsers.parse("a Subarray in intermediate obsState {obs_state}"))
def given_tmc_in_intermediate_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    obs_state: str,
    command_input_factory: JsonFactory,
):
    """Set up a TMC and ensure it is in the given ObsState."""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    log_events({subarray_node_low.subarray_node: "obsState"})
    subarray_node_low.move_to_on()
    set_subarray_to_given_obs_state(
        subarray_node_low, obs_state, event_tracer, command_input_factory
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        f'"a Subarray in intermediate obsState {obs_state}"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        f"is expected to be in {obs_state} obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState[obs_state],
    )


@when("I Abort it")
def invoke_abort_command(
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Send a Abort command to the subarray."""
    result_code, _ = subarray_node_low.execute_transition("Abort")
    assert result_code[0] == ResultCode.STARTED


@then(parsers.parse("the Subarray transitions to ABORTED obsState"))
def check_obs_state(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray is in the ABORTED obsState."""
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN STEP: '
        f'"the Subarray transitions to ABORTED obsState"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        f"is expected to be in ABORTING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN STEP: '
        f'"the Subarray transitions to ABORTED obsState"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        f"is expected to be in ABORTED obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.ABORTED
    )
