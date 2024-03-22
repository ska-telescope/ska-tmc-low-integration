"""Test module for TMC-MCCS handle invalid json functionality"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.mccs1
@scenario(
    "../features/tmc_mccs/xtp-34263_invalid_json_mccs.feature",
    "Invalid Station Id provided to MCCS controller",
)
def test():
    """."""


def update_assign_json(
    assign_json: str,
    station_id: int,
) -> str:
    """
    Returns a json with updated values for the given keys
    """
    assign_dict = json.loads(assign_json)

    assign_dict["mccs"]["subarray_beams"]["apertures"] = station_id
    return json.dumps(assign_dict)


@given("a Telescope consisting of TMC,MCCS,simulated SDP and simulated CSP")
def given_the_sut(central_node_low, subarray_node_low, simulator_factory):
    """
    Given a TMC and CSP in ON state
    """
    mccs_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_MASTER_DEVICE
    )

    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert subarray_node_low.subarray_devices["mccs_subarray"].ping() > 0
    assert mccs_master_sim.ping() > 0


@given("the Telescope is in the ON state")
def check_telescope_is_in_on_state(central_node_low, event_recorder) -> None:
    """Ensure telescope is in ON state."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=10,
    )


@given("the TMC subarray is in EMPTY obsState")
def subarray_in_empty_obsstate(subarray_node_low, event_recorder):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert subarray_node_low.subarray_node.obsState == ObsState.EMPTY


@when(
    parsers.parse(
        "I assign resources with invalid {station_id} to "
        + "the MCCS subarray using TMC"
    )
)
def invoke_assignresources(
    station_id: int,
    central_node_low,
    command_input_factory,
    subarray_id,
    stored_unique_id,
):
    """Invokes AssignResources command on TMC"""
    central_node_low.set_subarray_id(subarray_id)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_json_string = update_assign_json(
        input_json,
        station_id,
    )
    _, unique_id = central_node_low.store_resources(assign_json_string)
    stored_unique_id.append(unique_id)


@then(
    parsers.parse(
        "the MCCS controller should throw the error for invalid {station_id}"
    )
)
def invalid_command_rejection(station_id: int):
    """Mccs throws error"""
    assert (
        f"Cannot allocate resources: {station_id}"
    ) in pytest.command_result[1][0]

    assert pytest.command_result[0][0] == ResultCode.FAILED


@then("the MCCS subarray should remain in EMPTY ObsState")
def check_mccs_is_on(central_node_low, subarray_node_low, event_recorder):
    """A method to check MCCS controller and MCCS subarray states"""
    event_recorder.subscribe_event(central_node_low.mccs_master, "State")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("mccs_subarray"), "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsstate",
        ObsState.EMPTY,
    )


@then("the TMC propagate the error to the client")
def central_node_receiving_error(
    event_recorder, central_node_low, stored_unique_id
):
    """CN gets error"""
    unique_id = stored_unique_id[0]
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )

    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], Anything),
    )
    assert (
        "Exception occurred on the following devices: "
        + "ska_low/tm_leaf_node/mccs_master: Cannot allocate resources: 15"
        + "ska_low/tm_subarray_node/1: Timeout has occurred, command failed"
        in assertion_data["attribute_value"][1]
    )


@then("CSP,SDP Subarray transitions to ObsState IDLE")
def check_sdp_csp_obsstate(event_recorder, subarray_node_low):
    """Check SDP and CSP obsstate"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("csp_subarray"), "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )


@then("the TMC SubarrayNode stuck in RESOURCING")
def check_subarraynode_obsstate(event_recorder, subarray_node_low):
    """Check subarraynode obssate to be in RESOURCING"""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when("I issue the Abort command on TMC SubarrayNode")
def abort_is_invoked(subarray_node_low):
    """
    This method invokes abort command on tmc subarray
    """
    subarray_node_low.execute_transition("Abort")


@then("the CSP, SDP and TMC subarray transitions to obsState ABORTED")
def sdp_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check SDP subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@when("I issue the Restart command on TMC SubarrayNode")
def restart_is_invoked(subarray_node_low):
    """
    This method invokes restart command on tmc subarray
    """
    subarray_node_low.execute_transition("Restart")


@then("the CSP, SDP and TMC subarray transitions to obsState EMPTY")
def check_sdp_csp_subarray_obsstate(event_recorder, subarray_node_low):
    """Check SDP CSP and TMC Subarray obsstate to be EMPTY"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
