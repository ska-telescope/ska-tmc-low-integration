"""Test Error Propagation and Timeout for Configure command."""

import pytest
from pytest_bdd import given, parsers, scenario, then, when
import pytest
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.constant import (
    INTERMEDIATE_CONFIGURING_STATE_DEFECT,
    mccs_subarray_leaf_node,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_timeout_mccs.feature",
    "Timeout Error Reported by TMC Low Configure Command for"
    + " Defective MCCS Subarray",
)
def test_mccs_configure_command_timeout():
    """
    Test case to verify TMC-MCCS Configure Timeout functionality
    """


@given("the telescope is is ON state")
def check_telescope_is_in_on_state(subarray_node_low, event_recorder) -> None:
    """Ensure telescope is in ON state."""
    # Event Subscriptions
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "State"
    )
    subarray_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "State", DevState.ON
    )


@given("the TMC subarray is in the idle observation state")
def check_subarray_obs_state(
    subarray_node_low,
    event_recorder,
):
    """Method to check subarray is in IDLE obstate"""
    event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
    subarray_node_low.force_change_of_obs_state("IDLE")
    assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "obsState", ObsState.IDLE
        )
    
@when("the MCCS Subarray is identified as defective and configure command is "
    + "executed on the TMC Low")
def invoke_configure_command_with_mccs_defective(
    simulator_factory,
    command_input_factory,
    subarray_node_low,
    event_recorder,
    stored_unique_id,
):
    mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )
    # Preparing input files
    configure_input_str = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    # Inducing Fault
    mccs_subarray_sim.SetDefective(INTERMEDIATE_CONFIGURING_STATE_DEFECT)

    _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
    assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "obsState", ObsState.CONFIGURING
        )
    stored_unique_id.append(unique_id[0])
    

@then("the Configure command times out and reports an error")
def configure_command_reports_timeout(
    stored_unique_id,
    subarray_node_low,
    event_recorder,
):
    event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )
    assertion_data = event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (stored_unique_id[0], Anything),
        )
    assert (
        "Timeout has occurred, command failed"
        in assertion_data["attribute_value"][1]
    )
    assert (
        mccs_subarray_leaf_node in assertion_data["attribute_value"][1]
    )