"""Test module for TMC-CSP StartUp functionality"""
import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.constant import device_dict_low
from tests.resources.test_harness.helpers import get_master_device_simulators
from tests.resources.test_harness.utils.wait_helpers import Waiter

wait = Waiter(**device_dict_low)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/tmc_csp_startup.feature",
    "Start up the telescope having TMC and CSP subsystems",
)
def test_tmc_csp_startup_telescope():
    """
    Test case to verify TMC-CSP StartUp functionality
    """


@given("a Telescope consisting of TMC,CSP,simulated SDP and simulated MCCS")
def given_the_sut(central_node_low, simulator_factory):
    """
    Given a TMC

    Args:
        simulator_factory: fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
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


@when("I start up the telescope")
def move_telescope_to_on(central_node_low):
    """A method to turn on the telescope."""
    central_node_low.move_to_on()
    wait.set_wait_for_telescope_on()
    wait.wait(30)


@then("the CSP must go to ON state")
def check_csp_is_on(central_node_low, event_recorder):
    """A method to check CSP controller and CSP subarray states."""
    event_recorder.subscribe_event(central_node_low.csp_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "State"
    )
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


@then("telescope state is ON")
def check_telescope_state(central_node_low, event_recorder):
    """A method to check CentralNode.telescopeState"""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
