"""Test module for TMC-MCCS ShutDown functionality"""
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.constant import (
    mccs_controller,
    mccs_master_leaf_node,
    tmc_low_subarraynode1,
)
from tests.resources.test_harness.helpers import (
    get_device_simulator_with_given_name,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    wait_for_attribute_update,
)


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-35236_mccs_subsystem_unavailable.feature",
    "MCCS Controller report the error when one of the subarray"
    + " beam is unavailable",
)
def test_tmc_mccs_when_subsystem_unavailable():
    """
    Test case to verify TMC-MCCS error propagation
    when one of the mccs's subsystem subarray beam is unavailable.
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("a Telescope consisting of TMC,MCCS,emulated SDP and emulated CSP")
def check_tmc_and_mccs_is_on(tmc_low, event_recorder, simulator_factory):
    """
    Given a TMC and MCCS in ON state
    """
    simulated_devices = get_device_simulator_with_given_name(
        simulator_factory, ["csp master", "sdp master"]
    )
    if len(simulated_devices) == 2:
        csp_master_sim = simulated_devices[0]
        sdp_master_sim = simulated_devices[1]
        assert csp_master_sim.ping() > 0
        assert sdp_master_sim.ping() > 0
    assert tmc_low.central_node.central_node.ping() > 0
    assert tmc_low.central_node.mccs_master.ping() > 0
    assert tmc_low.subarray_node.subarray_devices["mccs_subarray"].ping() > 0

    event_recorder.subscribe_event(
        tmc_low.central_node.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(tmc_low.central_node.mccs_master, "State")
    event_recorder.subscribe_event(
        tmc_low.subarray_node.subarray_devices["mccs_subarray"], "State"
    )

    if tmc_low.central_node.telescope_state != "ON":
        tmc_low.central_node.move_to_on()

    assert event_recorder.has_change_event_occurred(
        tmc_low.central_node.mccs_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        tmc_low.subarray_node.subarray_devices["mccs_subarray"],
        "State",
        DevState.ON,
    )


@given("the telescope is in ON state")
def check_telescope_state_is_on(tmc_low, event_recorder):
    """A method to check CentralNode's telescopeState"""
    assert event_recorder.has_change_event_occurred(
        tmc_low.central_node.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("the TMC subarray is in EMPTY obsState")
def subarray_in_empty_obsstate(tmc_low, event_recorder):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    event_recorder.subscribe_event(
        tmc_low.subarray_node.subarray_node, "obsState"
    )
    assert tmc_low.subarray_node.subarray_node.obsState == ObsState.EMPTY


@when("one of the MCCS subarraybeam is made unavailable")
def mccs_subarraybeam_is_unavaiable(tmc_low):
    """Delete the MCCS's SubarrayBeam device"""
    tmc_low.delete_device_from_db(server_type="MCCS_SUBARRAYBEAM")
    tmc_low.RestartServer(server_type="MCCS_SUBARRAYBEAM")


@when(
    parsers.parse(
        "I assign resources with the {subarray_id} to the "
        + "TMC subarray using TMC"
    )
)
def invoke_assignresources(
    tmc_low, command_input_factory, subarray_id, stored_unique_id
):
    """Invokes AssignResources command on TMC"""
    tmc_low.central_node.set_subarray_id(subarray_id)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = tmc_low.central_node.perform_action(
        "AssignResources", input_json
    )
    stored_unique_id.append(unique_id[0])


@then("MCCS controller should throw the error and report to TMC")
def mccs_error_reporting(event_recorder, tmc_low, stored_unique_id):
    """
    Ensure that the MCCS controller throws an
    error for the subsystem unavailable
    and subscribe to the longRunningCommandResult event.
    """
    event_recorder.subscribe_event(
        tmc_low.central_node.mccs_master_leaf_node,
        "longRunningCommandResult",
    )
    assert wait_for_attribute_update(
        tmc_low.central_node.mccs_master_leaf_node,
        "longRunningCommandResult",
        "AssignResources",
        ResultCode.FAILED,
    )
    exception_message = (
        f"Exception occurred on device: {mccs_controller}: "
        + "The SubarrayBeam.assign_resources command has failed"
    )
    assert stored_unique_id[0].endswith("AssignResources")
    time.sleep(30)
    assertion_data = event_recorder.has_change_event_occurred(
        tmc_low.central_node.mccs_master_leaf_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(Anything, exception_message),
    )
    assert "AssignResources" in assertion_data["attribute_value"][0]
    assert exception_message in assertion_data["attribute_value"][1]


@then("TMC should propogate the error to client")
def central_node_receiving_error(event_recorder, tmc_low, stored_unique_id):
    """
    Ensure that the TMC propagates the error to the client and subscribe to
    the longRunningCommandResult event.
    """
    event_recorder.subscribe_event(
        tmc_low.central_node.central_node,
        "longRunningCommandResult",
        timeout=80.0,
    )
    expected_long_running_command_result = (
        stored_unique_id[0],
        "Exception occurred on the following devices: "
        + f"{mccs_master_leaf_node}: Exception occurred on device: "
        + f"{mccs_controller}: The SubarrayBeam.assign_resources command "
        + f"has failed{tmc_low_subarraynode1}: "
        + "Timeout has occurred, command failed",
    )

    assert event_recorder.has_change_event_occurred(
        tmc_low.central_node.central_node,
        "longRunningCommandResult",
        expected_long_running_command_result,
        lookahead=10,
    )


@then("the TMC SubarrayNode remains in ObsState RESOURCING")
def tmc_subarray_obsstate_resourcing(tmc_low, event_recorder):
    """Checks if SubarrayNode's obsState attribute value is RESOURCING"""
    assert event_recorder.has_change_event_occurred(
        tmc_low.subarray_node.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
