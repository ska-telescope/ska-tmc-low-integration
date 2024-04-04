"""Test case for verifying TMC TelescopeHealthState transition based on SDP
 Controller HealthState."""

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import HealthState

from tests.resources.test_harness.helpers import (
    get_device_simulator_with_given_name,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


@pytest.mark.tmc_sdp_unhappy_path
@scenario(
    "../features/tmc_sdp/xtp-34895_health_state_sdp.feature",
    "Verify TMC TelescopeHealthState transition based on SDP Controller"
    + "HealthState",
)
def test_telescope_state_sdp_controller():
    """This test case sets up a Telescope consisting of TMC-SDP, emulated CSP,
    and emulated MCCS. It then changes the health state of specified simulator
    devices and checks if the telescope's health state is
    updated accordingly."""


@given("a Telescope consisting of TMC-SDP, emulated CSP and emulated MCCS ")
def given_telescope_setup_with_simulators(central_node_low, simulator_factory):
    """
    Given a Telescope setup including TMC-SDP, emulated SDP, and emulated CSP.
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


@when(parsers.parse("The {devices} health state changes to {health_state} "))
def set_simulator_devices_health_states(
    devices, health_state, simulator_factory
):
    """A method to set HealthState value for the simulator devices"""
    # Split the devices string into individual devices
    devices_list = devices.split(",")
    health_state_list = health_state.split(",")

    sim_devices_list = get_device_simulator_with_given_name(
        simulator_factory, devices_list
    )
    for sim_device, sim_health_state_val in list(
        zip(sim_devices_list, health_state_list)
    ):
        # Check if the device is not the SDP controller
        if sim_device.device_name not in ["low-sdp/control/0"]:
            sim_device.SetDirectHealthState(HealthState[sim_health_state_val])


@then(parsers.parse("the telescope health state is {telescope_health_state}"))
def check_telescope_health_state(
    central_node_low, event_recorder, telescope_health_state
):
    """A method to check CentralNode.telescopehealthState attribute
    change after aggregation

    Args:
        central_node_low : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class_
        telescope_health_state (str): telescopehealthState value
    """
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeHealthState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeHealthState",
        HealthState[telescope_health_state],
    ), f"Expected telescopeHealthState to be \
        {HealthState[telescope_health_state]}"
