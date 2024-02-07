"""Test cases for Abort and Restart Command
    for low"""
import pytest

from tests.conftest import LOGGER
from tests.resources.test_support.common_utils.common_helpers import (
    Resource,
    Waiter,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    TmcHelper,
    prepare_json_args_for_centralnode_commands,
    tear_down,
)
from tests.resources.test_support.constant_low import (
    DEVICE_LIST_FOR_CHECK_DEVICES,
    DEVICE_OBS_STATE_ABORT_INFO,
    DEVICE_OBS_STATE_EMPTY_INFO,
    DEVICE_OBS_STATE_IDLE_INFO,
    DEVICE_STATE_OFF_INFO,
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    tmc_subarraynode1,
)


@pytest.mark.skip(
    reason="AssignResources and ReleaseResources"
    " functionalities are not yet"
    " implemented on mccs master leaf node."
)
@pytest.mark.SKA_low
def test_low_abort_restart_in_aborting(
    command_input_factory, central_node_low
):
    """Abort and Restart is executed."""
    assign_json = prepare_json_args_for_centralnode_commands(
        "command_assign_resources_low", command_input_factory
    )
    release_json = prepare_json_args_for_centralnode_commands(
        "command_release_resources_low", command_input_factory
    )
    tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

    try:
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)

        # Verify Telescope is Off/Standby
        assert central_node_low.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        # Invoke TelescopeOn() command on TMC
        central_node_low.move_to_on()

        # Verify State transitions after TelescopeOn
        assert central_node_low.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        # Invoke AssignResources() Command on TMC
        central_node_low.store_resources(assign_json)

        # Verify ObsState is IDLE
        assert central_node_low.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        # Invoke Abort() command on TMC
        central_node_low.subarray_node.Abort()
        Resource(central_node_low.subarray_node).assert_attribute(
            "obsState"
        ).equals("ABORTING")

        # Invoke Abort() command on TMC
        with pytest.raises(Exception):
            tmc_helper.invoke_abort()

        # Wait for the transition to complete
        the_waiter = Waiter()
        the_waiter.set_wait_for_specific_obsstate(
            "ABORTED", [tmc_subarraynode1]
        )
        the_waiter.wait(100)

        # Verify State transitions after Abort
        assert central_node_low.is_in_valid_state(
            DEVICE_OBS_STATE_ABORT_INFO, "obsState"
        )

        # Invoke Restart() command on TMC
        central_node_low.invoke_restart(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is EMPTY
        assert central_node_low.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Invoke TelescopeOff() command on TMC
        tmc_helper.set_to_off(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeOff
        assert central_node_low.is_in_valid_state(
            DEVICE_STATE_OFF_INFO, "State"
        )

        LOGGER.info("Test complete.")

    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
