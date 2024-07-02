"""Test TMC-MCCS Abort functionality in Configuring obstate"""
import json

import pytest
from pytest_bdd import given, scenario, then
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_eb_pb_ids,
)


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-53192_abort_in_configuring.feature",
    "Abort configuring MCCS using TMC",
)
def test_tmc_mccs_abort_in_configuring(central_node_low):
    """
    Test case to verify TMC-MCCS Abort functionality in CONFIGURING obsstate
    """
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0


@given("TMC and MCCS subarray are busy configuring")
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
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_str = json.loads(assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = update_eb_pb_ids(json.dumps(assign_str))
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("mccs_subarray"), "obsState"
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.force_change_of_obs_state(
        "CONFIGURING",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.CONFIGURING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )


# @when -> ../conftest.py


@then("the MCCS subarray should go into an aborted obsstate")
def mccs_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check MCCS subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.ABORTING,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.ABORTED,
    )


@then("the TMC subarray node obsState is transitioned to ABORTED")
def tmc_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
