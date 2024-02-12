"""Test cases for Abort and Restart Command
    for low"""


import pytest
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.at
@pytest.mark.SKA_low
def test_low_abort_restart_in_aborting(
    event_recorder, central_node_low, command_input_factory, subarray_node_low
):
    """Abort and Restart is executed."""
    # telescope_control = BaseTelescopeControl()
    # assign_json = json_factory("command_assign_resource_low")
    # release_json = json_factory("command_release_resource_low")
    # tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

    # try:
    #     tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)

    #     # Verify Telescope is Off/Standby
    #     assert telescope_control.is_in_valid_state(
    #         DEVICE_STATE_STANDBY_INFO, "State"
    #     )

    #     # Invoke TelescopeOn() command on TMC
    #     tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)

    #     # Verify State transitions after TelescopeOn
    #     assert telescope_control.is_in_valid_state(
    #         DEVICE_STATE_ON_INFO, "State"
    #     )

    #     # Check Subarray1 availability
    #     assert check_subarray1_availability(tmc_subarraynode1)

    #     # Invoke AssignResources() Command on TMC
    #     tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)

    #     # Verify ObsState is IDLE
    #     assert telescope_control.is_in_valid_state(
    #         DEVICE_OBS_STATE_IDLE_INFO, "obsState"
    #     )

    #     # Invoke Abort() command on TMC
    #     subarray_node = DeviceProxy(tmc_subarraynode1)
    #     subarray_node.Abort()
    #     Resource(tmc_subarraynode1).assert_attribute("obsState").equals(
    #         "ABORTING"
    #     )

    #     # Invoke Abort() command on TMC
    #     with pytest.raises(Exception):
    #         tmc_helper.invoke_abort()

    #     # Wait for the transition to complete
    #     the_waiter = Waiter()
    #     the_waiter.set_wait_for_specific_obsstate(
    #         "ABORTED", [tmc_subarraynode1]
    #     )
    #     the_waiter.wait(100)

    #     # Verify State transitions after Abort
    #     assert telescope_control.is_in_valid_state(
    #         DEVICE_OBS_STATE_ABORT_INFO, "obsState"
    #     )

    #     # Invoke Restart() command on TMC
    #     tmc_helper.invoke_restart(**ON_OFF_DEVICE_COMMAND_DICT)

    #     # Verify ObsState is EMPTY
    #     assert telescope_control.is_in_valid_state(
    #         DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    #     )

    #     # Invoke TelescopeOff() command on TMC
    #     tmc_helper.set_to_off(**ON_OFF_DEVICE_COMMAND_DICT)

    #     # Verify State transitions after TelescopeOff
    #     assert telescope_control.is_in_valid_state(
    #         DEVICE_STATE_OFF_INFO, "State"
    #     )

    #     LOGGER.info("Test complete.")

    # except Exception:
    #     tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)

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
    central_node_low.perform_action("AssignResources", assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    subarray_node_low.abort_subarray()

    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )

    subarray_node_low.restart_subarray()
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
