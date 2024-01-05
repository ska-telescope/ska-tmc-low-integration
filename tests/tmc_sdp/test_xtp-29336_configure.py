"""Test module for TMC-SDP Configure functionality"""
import json

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
    "../features/tmc_sdp/xtp-29336_configure.feature",
    "Configure a SDP subarray for a scan using TMC",
)
def test_tmc_sdp_configure(central_node_low):
    """
    Test case to verify TMC-SDP Configure functionality

    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
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


@given(parsers.parse("TMC subarray in obsState IDLE"))
def check_subarray_obs_state(
    subarray_node_low, central_node_low, event_recorder, command_input_factory
):
    """Method to check subarray is in IDLE obstate"""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(
    parsers.parse("I configure with {scan_type} to the subarray {subarray_id}")
)
def invoke_configure(
    central_node_low,
    subarray_node_low,
    scan_type,
    subarray_id,
    command_input_factory,
):
    """A method to invoke Configure command"""
    input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    input_json = json.loads(input_json)
    input_json["sdp"]["scan_type"] = scan_type
    central_node_low.set_subarray_id(subarray_id)
    subarray_node_low.store_configuration_data(argin=json.dumps(input_json))


@then(
    parsers.parse(
        "the SDP subarray {subarray_id} obsState is transitioned READY"
    )
)
def check_sdp_subarray_in_ready(
    central_node_low, subarray_node_low, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""
    central_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "SDP subarray scanType reflects correctly configured {scan_type}"
    )
)
def check_sdp_subarray_scan_type(subarray_node_low, event_recorder, scan_type):
    """A method to check SDP subarray obsstates"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "scanType"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "scanType",
        scan_type,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} obsState is transitioned to READY"
    )
)
def check_tmc_subarray_obs_state(
    central_node_low, subarray_node_low, event_recorder, subarray_id
):
    """A method to check TMC subarray obsstate"""
    central_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
