"""Test module for TMC-mccs AssignResources functionality"""
import time

import pytest
import tango
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)

db = tango.Database()

beam_device_strings = db.get_device_exported("low-mccs/beam/*")
station_beams = []
for device_str in beam_device_strings:
    device = tango.DeviceProxy(device_str)
    device.adminMode = 0
    station_beams.append(device)

station_device_strings = db.get_device_exported("low-mccs/station/*")
stations = []
for device_str in station_device_strings:
    device = tango.DeviceProxy(device_str)
    device.adminMode = 0
    stations.append(device)

subarray_device_strings = db.get_device_exported("low-mccs/subarray/*")
subarrays = []
for device_str in subarray_device_strings:
    device = tango.DeviceProxy(device_str)
    device.adminMode = 0
    subarrays.append(device)

subarray_beam_device_strings = db.get_device_exported(
    "low-mccs/subarraybeam/*"
)
subarray_beams = []
for device_str in subarray_beam_device_strings:
    device = tango.DeviceProxy(device_str)
    device.adminMode = 0
    subarray_beams.append(device)

controller = tango.DeviceProxy("low-mccs/control/control")
controller.adminmode = 0


@pytest.mark.aki
@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-30490_assign_resources_mccs.feature",
    "Assigning Resources to MCCS Subarray",
)
def test_assignresources_command(central_node_low):
    """BDD test scenario for verifying successful execution of
    the AssignResources command with TMC and mccs devices for pairwise
    testing."""
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0


@given("the Telescope is in the ON state")
def given_a_telescope_in_on_state(
    central_node_low, subarray_node_low, event_recorder
):
    """Checks if CentralNode's telescopeState attribute value is on."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.mccs_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.mccs_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "State",
        DevState.ON,
    )
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


@when(
    parsers.parse(
        "I assign resources with the {subarray_id} to the subarray using TMC"
    )
)
def invoke_assignresources(
    central_node_low,
    command_input_factory,
    subarray_id,
):
    """Invokes AssignResources command on TMC"""
    central_node_low.set_subarray_id(subarray_id)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.store_resources(input_json)
    time.sleep(3)


@then("the MCCS subarray obsState must transition to IDLE")
def mccs_subarray_idle(subarray_node_low, event_recorder):
    """Checks if mccs Subarray's obsState attribute value is IDLE"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("mccs_subarray"), "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.IDLE,
    )


@then("the TMC subarray obsState is transitioned to IDLE")
def tmc_subarray_idle(subarray_node_low, event_recorder):
    """Checks if SubarrayNode's obsState attribute value is IDLE"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
        lookahead=15,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.IDLE
    )
