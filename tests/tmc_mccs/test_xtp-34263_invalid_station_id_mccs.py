"""Test module for TMC-MCCS handle invalid json functionality"""
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_base.commands import ResultCode
from tango import DevState

from tests.conftest import updated_assign_str
from tests.resources.test_harness.constant import (
    mccs_master_leaf_node,
    tmc_low_subarraynode1,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    wait_for_attribute_update,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-34263_invalid_json_mccs.feature",
    "Invalid Station Id provided to MCCS controller",
)
def test_invalid_station_id_reporting_tmc_mccs_controller():
    """
    Test the behavior of the MCCS controller when an invalid station ID is
      provided.

    This test case checks that the MCCS controller correctly reports the error
      for an invalid station ID and that the system transitions to the expected
            states after the error occurs.

    """


@given("a Telescope consisting of TMC-MCCS, emulated SDP and emulated CSP")
def given_telescope_setup_with_simulators(central_node_low, simulator_factory):
    """
    Given a Telescope setup including TMC-MCCS, emulated SDP, and emulated CSP.
    Checks if all necessary simulator devices are reachable.
    """
    csp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_CSP_MASTER_DEVICE
    )
    sdp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_SDP_MASTER_DEVICE
    )
    assert csp_master_sim.ping() > 0
    assert sdp_master_sim.ping() > 0
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0


@given("the Telescope is in the ON state")
def check_telescope_is_in_on_state(central_node_low, event_recorder) -> None:
    """
    Ensure the Telescope is in the ON state and subscribe to the telescopeState
    event.
    """
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=8,
    )


@given("the TMC subarray is in EMPTY obsState")
def tmc_subarray_in_empty_obsstate(subarray_node_low, event_recorder):
    """
    Check if the TMC subarray's obsState attribute value is EMPTY
    and subscribe to the obsState event.
    """
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.EMPTY
    )


@when(
    parsers.parse(
        "I assign resources with invalid {station_id} to "
        + "the MCCS subarray using TMC with subarray_id {subarray_id}"
    )
)
def invoke_assignresources(
    station_id: int,
    central_node_low,
    command_input_factory,
    subarray_id,
    stored_unique_id,
):
    """
    Invoke AssignResources command on TMC with invalid station_id to the MCCS
    subarray.
    """
    central_node_low.set_subarray_id(subarray_id)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_json_string = updated_assign_str(
        input_json,
        int(station_id),
    )
    _, unique_id = central_node_low.perform_action(
        "AssignResources", assign_json_string
    )
    stored_unique_id.append(unique_id)


@then("the MCCS controller should throw the error for invalid station id")
def invalid_command_rejection(event_recorder, central_node_low):
    """
    Ensure that the MCCS controller throws an error for the invalid station ID
    and subscribe to the longRunningCommandResult event.
    """
    event_recorder.subscribe_event(
        central_node_low.mccs_master_leaf_node,
        "longRunningCommandResult",
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.mccs_master_leaf_node,
        "longRunningCommandResult",
    )
    assert wait_for_attribute_update(
        central_node_low.mccs_master_leaf_node,
        "longRunningCommandResult",
        "AssignResources",
        ResultCode.FAILED,
    )


@then("the MCCS subarray should remain in EMPTY ObsState")
def mccs_subarray_remains_in_empty_obsstate(event_recorder, subarray_node_low):
    """
    Check that the MCCS subarray remains in the EMPTY obsState.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.EMPTY,
        lookahead=8,
    )


@then("the TMC propogate the error to the client")
def central_node_receiving_error(
    event_recorder, central_node_low, stored_unique_id
):
    """
    Ensure that the TMC propagates the error to the client and subscribe to
    the longRunningCommandResult event.
    """
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult", timeout=80.0
    )
    exception_msg = (
        "Exception occurred on the following devices: "
        + f"{mccs_master_leaf_node}: Cannot allocate resources: 15 "
        + f"{tmc_low_subarraynode1}: Timeout has occurred, command failed"
    )
    expected_long_running_command_result = (
        stored_unique_id[0],
        exception_msg,
    )

    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        expected_long_running_command_result,
    )


@then("the TMC SubarrayNode remains in RESOURCING obsState")
def tmc_subarray_remains_in_resourcing_obsstate(
    event_recorder, subarray_node_low
):
    """
    Check that the TMC SubarrayNode remains in the RESOURCING obsState
    and subscribe to the obsState event.
    """
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
        lookahead=8,
    )


@when("I issue the Abort command on TMC SubarrayNode")
def abort_is_invoked(subarray_node_low):
    """
    Invoke the Abort command on the TMC SubarrayNode.
    """
    subarray_node_low.execute_transition("Abort")


@then("the TMC subarray transitions to obsState ABORTED")
def tmc_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Check that the TMC subarray transitions to the ABORTED obsState
    and subscribe to the obsState event.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@when("I issue the Restart command on TMC SubarrayNode")
def restart_is_invoked(subarray_node_low):
    """
    Invoke the Restart command on the TMC SubarrayNode.
    """
    subarray_node_low.execute_transition("Restart")


@then("the TMC subarray transitions to obsState EMPTY")
def check_tmc_subarray_is_in_empty_obsstate(event_recorder, subarray_node_low):
    """
    Check that the TMC subarray transitions to the EMPTY obsState
    and subscribe to the obsState event.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
