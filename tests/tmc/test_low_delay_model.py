"""
This module defines a Pytest BDD test scenario for checking the
delay value generation during the Configure command execution on a
Telescope Monitoring and Control (TMC) system
The scenario includes steps to set up the TMC, configure the subarray,
and checks whether CspSubarrayLeafNode starts generating delay value.
"""
import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    wait_for_updates_on_delay_model,
    wait_for_updates_stop_on_delay_model,
)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_low_delay_model.feature",
    "TMC generates delay values",
)
def test_low_delay_model():
    """
    Test whether delay value are generation on CSP Subarray Leaf Node.
    """


@given("the telescope is in ON state")
def given_telescope_is_in_on_state(central_node_low, event_recorder):
    """Method to check if telescope is in ON State"""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("subarray is in obsState IDLE")
def subarray_in_idle_obsstate(
    central_node_low, subarray_node_low, command_input_factory, event_recorder
) -> None:
    """Checks subarray is in obsState IDLE."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)

    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(ResultCode.OK.value)),
    )


@when("I configure the subarray")
def invoke_configure_command(
    subarray_node_low, command_input_factory, event_recorder
) -> None:
    """Invoke Configure command."""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(ResultCode.OK.value)),
    )


@then("CSP Subarray Leaf Node starts generating delay values")
def check_if_delay_values_are_generating(subarray_node_low) -> None:
    """Check if delay values are generating."""
    wait_for_updates_on_delay_model(subarray_node_low.csp_subarray_leaf_node)
    assert subarray_node_low.csp_subarray_leaf_node.delayModel != ""


@when("I end the observation")
def invoke_end_command(subarray_node_low, event_recorder) -> None:
    """Invoke End command."""
    subarray_node_low.end_observation()
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@then("CSP Subarray Leaf Node stops generating delay values")
def check_if_delay_values_are_not_generating(subarray_node_low) -> None:
    """Check if delay values are generating."""
    wait_for_updates_stop_on_delay_model(
        subarray_node_low.csp_subarray_leaf_node
    )
    assert subarray_node_low.csp_subarray_leaf_node.delayModel == ""
