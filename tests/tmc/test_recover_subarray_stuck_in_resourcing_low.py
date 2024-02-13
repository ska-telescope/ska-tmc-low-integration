"""Test cases for recovery of subarray stuck in RESOURCING
ObsState for low"""
import json
import time

import pytest
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import INTERMEDIATE_STATE_DEFECT

# assign_json = json_factory("command_assign_resource_low")
# release_json = json_factory("command_release_resource_low")
# try:
#     telescope_control = BaseTelescopeControl()
#     tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

#     # Verify Telescope is Off/Standby
#     assert telescope_control.is_in_valid_state(
#         DEVICE_STATE_STANDBY_INFO, "State"
#     )

#     # Invoke TelescopeOn() command on TMC
#     tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
#     LOGGER.info("TelescopeOn command is invoked successfully")

#     # Verify State transitions after TelescopeOn#
#     assert telescope_control.is_in_valid_state(
#         DEVICE_STATE_ON_INFO, "State"
#     )

#     the_waiter = Waiter()
#     # Invoke AssignResources() Command on TMC
#     LOGGER.info("Invoking AssignResources command on TMC CentralNode")
#     sdp_subarray = DeviceProxy(sdp_subarray1)
#     central_node = DeviceProxy(centralnode)
#     central_node.subscribe_event(
#         "longRunningCommandResult",
#         EventType.CHANGE_EVENT,
#         change_event_callbacks["longRunningCommandResult"],
#     )
#     sdp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

#     # Added this check to ensure that devices are running to avoid
#     # random test failures.
#     Resource(tmc_subarraynode1).assert_attribute("State").equals("ON")
#     Resource(tmc_subarraynode1).assert_attribute("obsState").equals(
#         "EMPTY"
#     )
#     the_waiter.set_wait_for_specific_obsstate(
#         "RESOURCING", [tmc_subarraynode1]
#     )
#     the_waiter.set_wait_for_specific_obsstate("IDLE", [csp_subarray1])
#     _, unique_id = central_node.AssignResources(assign_json)
#     the_waiter.wait(30)

#     sdp_subarray.SetDefective(json.dumps({"enabled": False}))

#     assertion_data = change_event_callbacks[
#         "longRunningCommandResult"
#     ].assert_change_event(
#         (unique_id[0], Anything),
#         lookahead=7,
#     )
#     assert "AssignResources" in assertion_data["attribute_value"][0]
#     assert (
#         "Timeout has occured, command failed"
#         in assertion_data["attribute_value"][1]
#     )
#     assert (
#         tmc_sdp_subarray_leaf_node in assertion_data["attribute_value"][1]
#     )

#     assert Resource(csp_subarray1).get("obsState") == "IDLE"

#     assert Resource(sdp_subarray1).get("obsState") == "RESOURCING"
#     sdp_subarray.SetDirectObsState(ObsState.EMPTY)
#     assert Resource(sdp_subarray1).get("obsState") == "EMPTY"
#     csp_subarray = DeviceProxy(csp_subarray1)
#     csp_subarray.ReleaseAllResources()
#     the_waiter.set_wait_for_specific_obsstate("EMPTY", [csp_subarray1])
#     the_waiter.set_wait_for_specific_obsstate("EMPTY", [tmc_subarraynode1])
#     the_waiter.wait(30)

#     assert telescope_control.is_in_valid_state(
#         DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
#     )

#     # Invoke TelescopeStandby() command on TMC#
#     tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)

#     # Verify State transitions after TelescopeStandby#
#     assert telescope_control.is_in_valid_state(
#         DEVICE_STATE_STANDBY_INFO, "State"
#     )
#     LOGGER.info("Test complete.")

# except Exception as e:
#     LOGGER.info(f"Exception occurred {e}")
#     tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@pytest.mark.pp
@pytest.mark.SKA_low
def test_recover_subarray_stuck_in_resourcing_low(
    event_recorder, central_node_low, command_input_factory, simulator_factory
):
    """AssignResources and ReleaseResources is executed."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
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
    csp_sim, _ = get_device_simulators(simulator_factory)
    csp_sim.SetDefective(json.dumps({"enabled": False}))
    central_node_low.perform_action("AssignResources", assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    time.sleep(2)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )
    csp_sim.SetDefective(json.dumps({"enabled": False}))
    csp_sim.SetDirectObsstate(ObsState.IDLE)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    central_node_low.subarray_node.Abort()
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
    central_node_low.subarray_node.Restart()

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@pytest.mark.pp
@pytest.mark.SKA_low
def test_recover_subarray_stuck_in_resourcing_with_sdp_empty_with_abort(
    event_recorder, central_node_low, command_input_factory, simulator_factory
):
    """AssignResources and ReleaseResources is executed."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
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
    csp_sim, _ = get_device_simulators(simulator_factory)
    csp_sim.SetDefective(json.dumps({"enabled": False}))
    central_node_low.perform_action("AssignResources", assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )
    csp_sim.SetDefective(json.dumps({"enabled": False}))
    csp_sim.SetDirectObsstate(ObsState.IDLE)

    central_node_low.subarray_node.Abort()
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
    central_node_low.subarray_node.Restart()

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@pytest.mark.SKA_low
def test_recover_subarray_stuck_in_resourcing_with_csp_empty_with_abort(
    event_recorder, central_node_low, command_input_factory, simulator_factory
):
    """AssignResources and ReleaseResources is executed."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
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
    csp_sim, _ = get_device_simulators(simulator_factory)
    csp_sim.SetDefective(json.dumps({"enabled": False}))
    central_node_low.perform_action("AssignResources", assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    time.sleep(2)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )
    csp_sim.SetDefective(json.dumps({"enabled": False}))
    csp_sim.SetDirectObsstate(ObsState.IDLE)

    central_node_low.subarray_node.Abort()
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
    central_node_low.subarray_node.Restart()

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@pytest.mark.skip(
    reason="AssignResources and ReleaseResources"
    " functionalities are not yet"
    " implemented on mccs master leaf node."
)
@pytest.mark.SKA_low
def test_recover_subarray_stuck_in_resourcing_with_abort(
    event_recorder, central_node_low, command_input_factory, simulator_factory
):
    """AssignResources and ReleaseResources is executed."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
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
    csp_sim, sdp_sim = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    csp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    central_node_low.perform_action("AssignResources", assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.EMPTY,
    )
    sdp_sim.SetDefective(json.dumps({"enabled": False}))
    central_node_low.subarray_node.ReleaseResources()
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
