"""
Test TMC-SDP Release Resources functionality.
"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import generate_eb_pb_ids
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/release_resources_to_sdp_subarray.feature",
    """Release resources from SDP Subarray using TMC""",
)
def test_tmc_sdp_release_resources():
    """
    Test case to verify TMC-SDP Releaseresources() functionality
    """


@given("a TMC and SDP")
def telescope_is_in_on_state(central_node_low):
    """ "A method to define TMC and SDP."""
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0


@given(parsers.parse("a subarray {subarray_id} in the IDLE obsState"))
def telescope_is_in_idle_state(
    central_node_low, event_recorder, command_input_factory, subarray_id
):
    """ "A method to move telescope into the IDLE state."""
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
    generate_eb_pb_ids(assign_input_json)
    central_node_low.store_resources(assign_input_json)
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(parsers.parse("I release all resources assigned to it"))
def release_resources_to_subarray(central_node_low, command_input_factory):
    """Method to release resources to subarray."""
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_low", command_input_factory
    )
    central_node_low.invoke_release_resources(release_input_json)


@then(
    parsers.parse("the SDP subarray {subarray_id} must be in EMPTY obsState")
)
def check_sdp_is_in_empty_obsstate(
    central_node_low, event_recorder, subarray_id
):
    """Method to check SDP is in EMPTY obsstate"""
    central_node_low.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(
        central_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse("TMC subarray {subarray_id} obsState transitions to EMPTY")
)
def check_tmc_is_in_idle_obsstate(
    central_node_low, event_recorder, subarray_id
):
    """Method to check TMC is is in EMPTY obsstate."""
    central_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
