"""
This module defines a Pytest BDD test scenario for checking the
delay value generation during the Configure command execution on a
Telescope Monitoring and Control (TMC) system
The scenario includes steps to set up the TMC, configure the subarray,
and checks whether Cspleafnode starts generating delay value.
"""
import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    wait_till_delay_values_are_populated,
)

TIMEOUT = 15


@pytest.mark.ms
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_low_delay_model.feature",
    "TMC generates delay values",
)
def test_low_delay_model():
    """
    Test whether delay value are generation on Cspleafnode.
    """


@given("the telescope is in ON state")
def check_tmc_csp_state_is_on(central_node_low, event_recorder):
    """Move telescoep to on state"""
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
def check_subarray_is_in_idle_obsstate(
    central_node_low, command_input_factory, event_recorder
) -> None:
    """Checks subarray is in obsState IDLE."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.store_resources(assign_input_json)

    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when("I configure the subarray")
def invoke_configure_command(
    subarray_node_low, command_input_factory, event_recorder
) -> None:
    """Invoke Configure command."""
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.store_configuration_data(configure_input_json)


@then("CSP subarray leaf node starts generating delay values")
def check_if_delay_values_are_generating(
    subarray_node_low,
) -> None:
    """Check if delay values are generating."""
    wait_till_delay_values_are_populated(
        subarray_node_low.csp_subarray_leaf_node
    )
    assert subarray_node_low.csp_subarray_leaf_node.delayModel not in [
        "",
        "no_value",
    ]
