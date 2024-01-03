"""
Test TMC-SDP Configure functionality.
"""
import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)

LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29336_configure.feature",
    """Configure a SDP subarray for a scan using TMC""",
)
def test_configure_sdp_subarray():
    """
    Test case to verify TMC-SDP Configure() functionality
    """


@given("the Telescope is in ON state")
def given_a_tmc(central_node_low, event_recorder):
    """
    Given a TMC
    """
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )

    if central_node_low.telescope_state != "ON":
        central_node_low.move_to_on()

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
    subarray_node_low.execute_transition(
        "Configure", argin=json.dumps(input_json)
    )


@then(parsers.parse("the SDP subarray {subarray_id} obsState is READY"))
def check_sdp_subarray_in_ready(
    central_node_low, subarray_node_low, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "obsState"
    )

    central_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
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
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")

    central_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
