"""Test cases for Abort and Restart Command
    for low"""


import pytest
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.SKA_low
def test_low_abort_restart_in_aborting(
    event_recorder, central_node_low, command_input_factory, subarray_node_low
):
    """Abort and Restart is executed."""

    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")

    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    central_node_low.perform_action("AssignResources", assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    subarray_node_low.abort_subarray()

    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )
    with pytest.raises(Exception):
        subarray_node_low.restart_subarray()
