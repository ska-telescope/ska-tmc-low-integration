"""Test module to test TMC-MCCS End functionality."""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-31010_end_command.feature",
    "End configure from MCCS Subarray",
)
def test_tmc_mccs_end_functionality():
    """
    Test case to verify TMC-MCCS observation End functionality
    """


@given("the Telescope is in the ON state")
def check_telescope_is_in_on_state(central_node_low, event_recorder) -> None:
    """Ensure telescope is in ON state."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=10,
    )


@given(parsers.parse("the obsState of subarray is READY"))
def move_subarray_node_to_ready_obsstate(
    central_node_low,
    subarray_node_low,
    event_recorder,
    command_input_factory,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("mccs_subarray"), "obsState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.store_configuration_data(configure_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=10,
    )


@when("I issue End command with the {subarray_id} to the subarray using TMC")
def invoke_end_command(
    subarray_node_low, central_node_low, subarray_id
) -> None:
    """Invoke End command."""
    central_node_low.set_subarray_id(subarray_id)
    subarray_node_low.execute_transition("End")


@then("the MCCS subarray is transitioned to IDLE obsState")
def check_if_mccs_subarray_moved_to_idle_obsstate(
    subarray_node_low, event_recorder
):
    """Ensure Mccs subarray is moved to IDLE obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )


@then("TMC subarray is transitioned to IDLE obsState")
def check_if_tmc_subarray_moved_to_idle_obsstate(
    subarray_node_low, event_recorder: EventRecorder
) -> None:
    """Ensure TMC Subarray is moved to IDLE obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )
