"""Test case for verifying TMC TelescopeHealthState transition based on MCCS
 Controller HealthState."""
import json

import pytest
from pytest_bdd import given, parsers, scenario, when
from ska_tango_base.control_model import HealthState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.helpers import (
    get_device_simulator_with_given_name,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory


# Adjust the health thresholds on the controller to force it into DEGRADED
# state
def adjust_controller_to_degraded_state(controller):
    """
    Adjusts the health thresholds on the controller to
      force it into DEGRADED state.

    Args:
        controller: The controller instance to adjust.

    Returns:
        None
    """
    health_params = {"stations_degraded_threshold": 0}
    controller.healthModelParams = json.dumps(health_params)


@pytest.mark.xfail(
    reason="The test is marked as xfail due to existing issues"
    + "with health in MCCS, which prevent the controller from entering a"
    + "DEGRADED state. This is a temporary measure until the underlying "
    + "issues are fixed."
)
@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-34965_healthstate_mccs.feature",
    "Verify CentralNode TelescopeHealthState",
)
def test_telescope_state_mccs_controller():
    """This test case sets up a Telescope consisting of TMC-MCCS, emulated CSP,
    and emulated SDP. It then changes the health state of specified simulator
    devices and checks if the telescope's health state is
    updated accordingly."""


@given("a Telescope consisting of TMC, MCCS, simulated CSP and simulated SDP")
def given_telescope_setup_with_simulators(
    central_node_low: CentralNodeWrapperLow,
    simulator_factory: SimulatorFactory,
):
    """Method to check TMC real devices and sub-system simulators

    Args:
        central_node_low (CentralNodeWrapperLow): Fixture for a
        TMC CentralNode under test
        simulator_factory (SimulatorFactory): Fixture for SimulatorFactory
        class, which provides simulated subarray and master devices
    """
    simulated_devices = get_device_simulator_with_given_name(
        simulator_factory, ["csp master", "sdp master"]
    )
    csp_master_sim, sdp_master_sim = simulated_devices
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.mccs_master.ping() > 0
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0
    assert csp_master_sim.ping() > 0
    assert sdp_master_sim.ping() > 0


@when(parsers.parse("The {devices} health state changes to {health_state}"))
def set_simulator_devices_health_states(
    devices: str,
    health_state: str,
    simulator_factory: SimulatorFactory,
    controller,
):
    """Method to set the health state of specified simulator devices.

    Args:
        devices (list): Names of the devices whose health state will change.
        health_state (list): The new health states for the devices.
        simulator_factory (SimulatorFactory): Fixture for SimulatorFactory
          class.
        controller: The controller instance to adjust.
    """
    adjust_controller_to_degraded_state(controller)
    # Split the devices string into individual devices
    devices_list = devices.split(",")
    health_state_list = health_state.split(",")

    sim_devices_list = get_device_simulator_with_given_name(
        simulator_factory, devices_list
    )
    for sim_device, sim_health_state_val in list(
        zip(sim_devices_list, health_state_list)
    ):
        # Check if the device is not the Mccs controller
        if sim_device.dev_name not in ("low-mccs/control/control"):
            sim_device.SetDirectHealthState(HealthState[sim_health_state_val])


# @then -> ../conftest.py
