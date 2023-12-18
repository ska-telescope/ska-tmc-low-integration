"""
This module defines a Pytest BDD test scenario for the successful execution of
Abort command of a Low Telescope Subarray in the Telescope Monitoring
and Control (TMC) system.
"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState

from tests.resources.test_support.common_utils.result_code import ResultCode
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
def given_tmc(subarray_node_low, event_recorder, obs_state):
    """Set up a TMC and ensure it is in the given ObsState."""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    subarray_node_low.move_to_on()
    subarray_node_low.force_change_of_obs_state(obs_state)

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState[obs_state],
    )


@given(parsers.parse("a Subarray in intermediate obsState {obs_state}"))
def given_tmc_in_intermediate_obsstate(
    subarray_node_low, event_recorder, obs_state, command_input_factory
):
    """Set up a TMC and ensure it is in the given ObsState."""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    subarray_node_low.move_to_on()
    set_subarray_to_given_obs_state(
        subarray_node_low, obs_state, event_recorder, command_input_factory
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState[obs_state],
    )


@when("I Abort it")
def invoke_abort_command(
    subarray_node_low,
):
    """Send a Abort command to the subarray."""
    result_code, _ = subarray_node_low.execute_transition("Abort")
    assert result_code[0] == ResultCode.STARTED


@then(parsers.parse("the Subarray transitions to ABORTED obsState"))
def check_obs_state(
    subarray_node_low,
    event_recorder,
):
    """Verify that the subarray is in the ABORTED obsState."""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
        lookahead=15,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
        lookahead=15,
    )
