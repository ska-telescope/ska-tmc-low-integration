"""
Test case to verify error propagation functionality for the Configure command
 of Mccsleafnodes.
This test case verifies that when the MCCS Subarray is identified as defective,
 and the Configure command is executed on the TMC Low, the Configure command
   reports an error.
"""
import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    mccs_subarray1,
    mccs_subarray_leaf_node,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)


@pytest.mark.SKA_low
@pytest.mark.test
@scenario(
    "../features/tmc/check_error_propagation_mccs.feature",
    "Error Propagation Reported by TMC Low Configure Command for"
    + " Defective MCCS Subarray",
)
def test_mccs_configure_command_error_propagation():
    """
    Test case to verify TMC-MCCS Error Propagation functionality.
    """


@given("the telescope is is ON state")
def check_telescope_is_in_on_state(subarray_node_low, event_recorder) -> None:
    """
    Ensure telescope is in ON state.
    """
    # Event Subscriptions
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "State")
    subarray_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "State", DevState.ON
    )


@given("the TMC subarray is in the idle observation state")
def check_subarray_obs_state(
    subarray_node_low,
    event_recorder,
):
    """
    Method to check subarray is in IDLE observation state.
    """
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    subarray_node_low.force_change_of_obs_state("IDLE")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.IDLE
    )


@when("Configure command is invoked on a defective MCCS Subarray")
def invoke_configure_command_with_mccs_defective(
    simulator_factory,
    command_input_factory,
    subarray_node_low,
    event_recorder,
    stored_unique_id,
):
    """
    Invoke the Configure command with the MCCS Subarray identified as defective

    This method prepares the input files, induces a fault in the MCCS Subarray
      simulator,
    and executes the Configure command on the TMC Low. It asserts that the
      subarray is in the CONFIGURING observation state after the
        command execution.
    """
    mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    # Preparing input files
    configure_input_str = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    # Inducing Fault
    #
    mccs_subarray_sim.SetDefective(ERROR_PROPAGATION_DEFECT)

    _, unique_id = subarray_node_low.execute_transition(
        "Configure", configure_input_str
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.CONFIGURING
    )
    stored_unique_id.append(unique_id[0])


@then(
    "the command failure is reported by subarray with appropriate"
    + " error message"
)
def configure_command_reports_error_propagate(
    stored_unique_id,
    subarray_node_low,
    event_recorder,
):
    """
    Verify that the Configure command reports an error.

    This method subscribes to the 'longRunningCommandResult' event and asserts
      that the command times out and reports an error message indicating a
        error has propagated.
    """
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    assertion_data = event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (stored_unique_id[0], Anything),
    )
    assert (
        "Exception occurred on the following devices:"
        + f" {mccs_subarray_leaf_node}:"
        + " Exception occurred on device:"
        + f" {mccs_subarray1}:"
        + ' . Event data is: [3, ""]\n'
        in assertion_data["attribute_value"][1]
    )
    assert mccs_subarray_leaf_node in assertion_data["attribute_value"][1]
