"""Test TMC-SDP Abort functionality in RESOURCING obsState"""

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    update_eb_pb_ids,
)


@pytest.mark.test1
@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/abort_resourcing_tmc_sdp.feature",
    "Abort invocation using TMC",
)
def test_tmc_sdp_abort_stuck_in_resourcing(central_node_low):
    """
    Test case to verify TMC-SDP Abort functionality in RESOURCING obsState
    """
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0


@given("TMC and SDP subarray busy assigning resources")
def telescope_is_in_resourcing_obsstate(
    central_node_low, event_recorder, command_input_factory, sub
):
    """A method to check if telescope in is resourcing obsSstate."""
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
    input_json = update_eb_pb_ids(assign_input_json)
    central_node_low.perform_action("AssignResources", input_json)

    event_recorder.subscribe_event(
        central_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.RESOURCING,
    )


@when("I command it to Abort")
def abort_is_invoked(subarray_node_low):
    """
    This method invokes abort command on tmc subarray
    """
    subarray_node_low.subarray_abort()


@then("the SDP subarray should go into an aborted obsstate")
def sdp_subarray_is_in_aborted_obsstate(central_node_low, event_recorder):
    """
    Method to check SDP subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )


@then("the TMC subarray obsState transitions to ABORTED")
def tmc_subarray_is_in_aborted_obsstate(central_node_low, event_recorder):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
