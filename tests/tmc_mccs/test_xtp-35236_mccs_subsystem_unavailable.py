"""Test module for TMC-MCCS ShutDown functionality"""

import pytest
from pytest_bdd import given, scenario

# then, when
from ska_control_model import ObsState
from tango import DevState


@pytest.mark.tmc_mccs
@scenario(
    "../features/xtp-35263_subsystem_unavailable.feature",
    "Switch off the telescope having TMC and MCCS subsystems",
)
def test_tmc_mccs_error_propagation_when_subsystem_unavailable():
    """
    Test case to verify TMC-MCCS error propagation
    when one of the subarray beam is unavailable.
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("a Telescope consisting of TMC,MCCS,emulated SDP and emulated CSP")
def check_tmc_and_mccs_is_on(central_node_low, event_recorder):
    """
    Given a TMC and MCCS in ON state
    """
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.mccs_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "State"
    )

    if central_node_low.telescope_state != "ON":
        central_node_low.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_low.mccs_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["mccs_subarray"],
        "State",
        DevState.ON,
    )


@given("the telescope is in ON state")
def check_telescope_state_is_on(central_node_low, event_recorder):
    """A method to check CentralNode's telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("the obsState of subarray is EMPTY")
def subarray_in_empty_obsstate(subarray_node_low, event_recorder):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert subarray_node_low.subarray_node.obsState == ObsState.EMPTY
