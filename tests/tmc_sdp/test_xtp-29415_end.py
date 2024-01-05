"""Test module for TMC-SDP End functionality"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29415_end.feature",
    "End configure from SDP Subarray using TMC",
)
def test_tmc_sdp_end(central_node_low):
    """
    Test case to verify TMC-SDP End functionality

    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
        - "subarray_node": fixture for a TMC SubarrayNode under test
    """
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0


@given("the Telescope is in ON state")
def telescope_is_in_on_state(central_node_low, event_recorder):
    """Move the telescope to the ON state and verify the state change.

    Args:
        central_node_low (CentralNodeLow): An instance of the CentralNodeLow
        class representing the central node.
        event_recorder (EventRecorder): An instance of the EventRecorder class
        for recording events.

    """
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("a subarray {subarray_id} in the READY obsState"))
def check_subarray_obs_state(
    central_node_low,
    subarray_node_low,
    command_input_factory,
    subarray_id,
    event_recorder,
):
    """Method to check subarray is in READY obstate"""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )

    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )

    central_node_low.set_subarray_id(subarray_id)
    subarray_node_low.force_change_of_obs_state(
        "READY",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when(parsers.parse("I issue End command to the subarray {subarray_id}"))
def invoke_end(central_node_low, subarray_node_low, subarray_id):
    """A method to invoke End command"""
    central_node_low.set_subarray_id(subarray_id)
    subarray_node_low.end_observation("End")


@then(
    parsers.parse(
        "the SDP subarray {subarray_id} transitions to IDLE obsState"
    )
)
def check_sdp_subarray_obs_state(
    central_node_low, subarray_node_low, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstates"""
    central_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@then(parsers.parse("TMC subarray {subarray_id} transitions to IDLE obsState"))
def check_tmc_subarray_obs_state(
    central_node_low, subarray_node_low, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstates"""

    central_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
