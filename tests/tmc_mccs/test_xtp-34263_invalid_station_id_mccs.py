"""Test module for TMC-MCCS handle invalid json functionality"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@scenario(
    "../features/tmc_mccs/xtp-34263_invalid_json_mccs.feature",
    "Invalid Station Id provided to MCCS Subarray",
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


@given(
    "Given a Telescope consisting of TMC,MCCS,simulated SDP and simulated CSP"
)
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
        "I assign resources with invalid {station_id} to the MCCS subarray"
        + "using TMC"
    )
)
def invoke_assignresources(
    station_id: int,
    central_node_low,
    command_input_factory,
    subarray_id,
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
    central_node_low.store_resources(assign_json_string)


@then("the MCCS subarray should throw the error for invalid station id")
def invalid_command_rejection():
    """Mccs throws error"""
    assert (
        "JSON validation error: data is not compliant"
    ) in pytest.command_result[1][0]

    assert pytest.command_result[0][0] == ResultCode.REJECTED
