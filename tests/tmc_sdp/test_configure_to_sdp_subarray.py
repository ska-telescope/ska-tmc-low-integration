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
@pytest.mark.configure
@scenario(
    "../features/tmc_sdp/configure_to_sdp_subarray.feature",
    """Configure a SDP subarray for a scan using TMC""",
)
def test_configure_sdp_subarray():
    """
    Test case to verify TMC-SDP Configure() functionality
    """


@given("the Telescope is in ON state")
def telescope_is_in_on_state(central_node_low, event_recorder):
    """Move the telescope to the ON state and verify the state change."""
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
    central_node_low, event_recorder, command_input_factory
):
    """Method to check subarray is in IDLE obstate"""
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(
    parsers.parse("I configure with {scan_type} to the subarray {subarray_id}")
)
def configure_sdp_subarray(
    central_node_low,
    scan_type,
    subarray_node_low,
    command_input_factory,
    subarray_id,
):
    """Method to configure SDP subarray."""
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    configure_input_json = json.loads(configure_input_json)
    configure_input_json["sdp"]["scan_type"] = scan_type
    central_node_low.set_subarray_id(subarray_id)

    subarray_node_low.execute_transition(
        "Configure", argin=json.dumps(configure_input_json)
    )


@then(parsers.parse("the SDP subarray {subarray_id} obsState is READY"))
def check_sdp_subarray_in_ready(
    central_node_low, subarray_node, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "obsState"
    )

    central_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} obsState is transitioned to READY"
    )
)
def check_tmc_subarray_obs_state(
    central_node_low, subarray_node, event_recorder, subarray_id
):
    """A method to check TMC subarray obsstate"""
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

    central_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
