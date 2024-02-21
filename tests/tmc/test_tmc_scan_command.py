"""
This module defines a Pytest BDD test scenario for the successful execution of
Scan Command of a Low Telescope Subarray in the Telescope Monitoring and
Control (TMC) system.
"""
import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.constant import tmc_low_subarraynode1
from tests.resources.test_support.common_utils.common_helpers import Waiter
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_scan_command.feature",
    "Successful Execution of Scan Command on Low Telescope Subarray in TMC",
)
def test_tmc_mccssln_scan_command():
    """BDD test scenario for verifying successful execution of
    the Low Scan command in a TMC."""


@given("a TMC")
def given_tmc(central_node_low, event_recorder):
    """Set up a TMC and ensure it is in the ON state."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given("a subarray in READY obsState")
def given_subarray_in_ready(
    command_input_factory,
    central_node_low,
    subarray_node_low,
    event_recorder,
):
    """Set up a subarray in the READY obsState."""
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.perform_action("AssignResources", assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.store_configuration_data(configure_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when("I command it to scan for a given period")
def send_scan(
    command_input_factory,
    subarray_node_low,
):
    """Send a Scan command to the subarray."""
    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    subarray_node_low.execute_transition("Scan", scan_input_json)


@then("the subarray must be in the SCANNING obsState until finished")
def check_scan_completion(
    subarray_node_low,
    event_recorder,
):
    """Verify that the subarray is in the SCANNING obsState."""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate("READY", [tmc_low_subarraynode1])
    the_waiter.wait(200)
