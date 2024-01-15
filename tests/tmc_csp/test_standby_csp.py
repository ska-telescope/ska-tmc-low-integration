"""Test module for TMC-SDP ShutDown functionality"""
import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.helpers import get_master_device_simulators


@pytest.mark.aki
@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/tmc_csp_standby.feature",
    "Standby the telescope having TMC and CSP subsystems",
)
def test_tmc_sdp_standby_telescope():
    """
    Test case to verify TMC-CSP Standby functionality
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("a Telescope consisting of TMC,CSP,simulated SDP and simulated MCCS")
def check_tmc_and_sdp_is_on(
    central_node_low, event_recorder, simulator_factory
):
    """
    Given a TMC and CSP in ON state
    """
    (
        _,
        sdp_master_sim,
    ) = get_master_device_simulators(simulator_factory)

    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0
    assert sdp_master_sim.ping() > 0
    central_node_low.csp_master.adminMode = 0
    central_node_low.csp_subarray1.adminMode = 0
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.csp_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "State"
    )

    if central_node_low.telescope_state != "ON":
        central_node_low.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_low.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )


@given("telescope state is ON")
def check_telescope_state_is_on(central_node_low, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@when("I put the telescope to STANDBY")
def move_sdp_to_standby(central_node_low):
    """A method to put SDP to STANDBY"""
    central_node_low.set_standby()


@then("telescope state is STANDBY")
def check_telescope_state_standby(central_node_low, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.STANDBY,
    )
