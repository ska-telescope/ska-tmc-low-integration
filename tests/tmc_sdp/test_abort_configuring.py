"""Test TMC-SDP Abort functionality in Configuring obstate"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_eb_pb_ids,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-30127_abort_configuring.feature",
    "Abort configuring SDP using TMC",
)
def test_tmc_sdp_abort_in_configuring(central_node_low):
    """
    Test case to verify TMC-SDP Abort functionality in CONFIGURING obsState
    """
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0


@given(
    parsers.parse(
        "TMC subarray {subarray_id} and SDP subarray {subarray_id} busy"
        + " configuring"
    )
)
def subarray_is_in_configuring_obsstate(
    central_node_low,
    event_recorder,
    command_input_factory,
    subarray_node_low,
    subarray_id,
):
    """A method to check if telescope is in CONFIGURING obsState."""
    central_node_low.set_subarray_id(subarray_id)
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_str = json.loads(assign_input_json)
    # Adding this to get an event of ObsState CONFIGURING from SDP
    assign_str["sdp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2
    assign_input_json = update_eb_pb_ids(json.dumps(assign_str))
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")

    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.force_change_of_obs_state(
        "CONFIGURING",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.CONFIGURING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )


@when("I command it to Abort")
def invoke_abort(subarray_node_low):
    """
    This method invokes abort command on tmc subarray
    """
    subarray_node_low.abort_subarray()


@then("the SDP subarray transitions to ObsState ABORTED")
def sdp_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check SDP subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )


@then("the subarray transitions to ObsState ABORTED")
def tmc_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
