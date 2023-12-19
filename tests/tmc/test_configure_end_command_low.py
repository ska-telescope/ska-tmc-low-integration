"""Test cases for Configure and End Command
    for low"""
import json
import time
from copy import deepcopy

import pytest
from ska_tango_base.control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DeviceProxy, EventType

from tests.conftest import LOGGER, TIMEOUT
from tests.resources.test_support.common_utils.common_helpers import Waiter
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
    check_subarray1_availability,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    TmcHelper,
    tear_down,
)
from tests.resources.test_support.constant_low import (
    COMMAND_NOT_ALLOWED_DEFECT,
    DEVICE_LIST_FOR_CHECK_DEVICES,
    DEVICE_OBS_STATE_EMPTY_INFO,
    DEVICE_OBS_STATE_IDLE_INFO,
    DEVICE_OBS_STATE_READY_INFO,
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    INTERMEDIATE_STATE_DEFECT,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    csp_subarray1,
    sdp_subarray1,
    tmc_csp_subarray_leaf_node,
    tmc_sdp_subarray_leaf_node,
    tmc_subarraynode1,
)

tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)
telescope_control = BaseTelescopeControl()


@pytest.mark.skip(
    reason="AssignResources and ReleaseResources"
    " functionalities are not yet"
    " implemented on mccs master leaf node."
)
@pytest.mark.SKA_low
def test_configure_end_low(json_factory):
    """Configure and End is executed."""
    assign_json = json_factory("command_assign_resource_low")
    release_json = json_factory("command_release_resource_low")
    configure_json = json_factory("command_Configure_low")
    try:
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        # Invoke TelescopeOn() command on TMC CentralNode
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )
        LOGGER.info("TelescopeOn command is executed.")
        # Check Subarray1 availability
        assert check_subarray1_availability(tmc_subarraynode1)
        csp_subarray = DeviceProxy(tmc_csp_subarray_leaf_node)
        # Invoke AssignResources() Command on TMC
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )
        LOGGER.info("AssignResources command is executed.")
        LOGGER.info(f"The Obstate is:{csp_subarray.cspSubarrayObsState}")
        LOGGER.info(f"DelayModel is:{csp_subarray.delayModel}")
        # Invoke Configure() Command on TMC
        tmc_helper.configure_subarray(
            configure_json, **ON_OFF_DEVICE_COMMAND_DICT
        )
        LOGGER.info(f"The Obstate is:{csp_subarray.cspSubarrayObsState}")

        time.sleep(1)
        waiter = Waiter(**ON_OFF_DEVICE_COMMAND_DICT)
        waiter.set_wait_for_delayvalue()
        waiter.wait(TIMEOUT)
        LOGGER.info(f"DelayModel is:{csp_subarray.delayModel}")

        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )
        LOGGER.info("Configure command is executed.")
        LOGGER.info(f"The Obstate is:{csp_subarray.cspSubarrayObsState}")
        LOGGER.info(f"DelayModel is:{csp_subarray.delayModel}")
        # Teardowning
        # Invoke End() Command on TMC
        tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )
        LOGGER.info("End command is executed.")
        LOGGER.info(f"The Obstate is:{csp_subarray.cspSubarrayObsState}")
        LOGGER.info(f"DelayModel is:{csp_subarray.delayModel}")
        # Invoke ReleaseResources() command on TMC
        tmc_helper.invoke_releaseResources(
            release_json, **ON_OFF_DEVICE_COMMAND_DICT
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )
        LOGGER.info("ReleaseResources command is executed.")
        # Invoke Standby() command on TMC
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
    except Exception as e:
        LOGGER.exception("The exception is: %s", e)
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@pytest.mark.skip(
    reason="AssignResources and ReleaseResources"
    " functionalities are not yet"
    " implemented on mccs master leaf node."
)
@pytest.mark.SKA_low
def test_configure_timeout_and_error_propagation_csp(
    json_factory, change_event_callbacks
):
    """Verify timeout exception raised when csp set to defective."""
    assign_json = json_factory("command_assign_resource_low")
    release_json = json_factory("command_release_resource_low")
    configure_json = json_factory("command_Configure_low")
    try:
        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        # Invoke TelescopeOn() command on TMC
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        # Invoke AssignResources() Command on TMC
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify transitions after AssignResources command
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        subarray_node_proxy = DeviceProxy(tmc_subarraynode1)
        subarray_node_proxy.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        csp_subarray = DeviceProxy(csp_subarray1)
        csp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

        # Invoking Configure command
        device_params = deepcopy(ON_OFF_DEVICE_COMMAND_DICT)
        device_params["set_wait_for_obsstate"] = False
        result_code, unique_id = tmc_helper.configure_subarray(
            configure_json, **device_params
        )
        assert unique_id[0].endswith("Configure")
        assert result_code[0] == ResultCode.QUEUED

        assertion_data = change_event_callbacks[
            "longRunningCommandResult"
        ].assert_change_event(
            (unique_id[0], Anything),
            lookahead=7,
        )

        assert "Configure" in assertion_data["attribute_value"][0]
        assert (
            "Timeout has occured, command failed"
            in assertion_data["attribute_value"][1]
        )
        assert (
            tmc_csp_subarray_leaf_node in assertion_data["attribute_value"][1]
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(ResultCode.FAILED.value)),
            lookahead=4,
        )

        csp_subarray.SetDefective(json.dumps({"enabled": False}))

        # Emulating Csp Subarray going back to READY state after failure
        csp_subarray.SetDirectObsState(ObsState.READY)

        # Tear Down
        csp_sln = DeviceProxy(tmc_csp_subarray_leaf_node)
        csp_sln.End()

        tear_down(
            release_json, raise_exception=False, **ON_OFF_DEVICE_COMMAND_DICT
        )

    except Exception as e:
        LOGGER.exception("The exception is: %s", e)
        tear_down(
            release_json, raise_exception=True, **ON_OFF_DEVICE_COMMAND_DICT
        )


@pytest.mark.skip(
    reason="AssignResources and ReleaseResources"
    " functionalities are not yet"
    " implemented on mccs master leaf node."
)
@pytest.mark.SKA_low
def test_configure_timeout_sdp(json_factory, change_event_callbacks):
    """Verify timeout exception raised when csp set to defective."""
    assign_json = json_factory("command_assign_resource_low")
    release_json = json_factory("command_release_resource_low")
    configure_json = json_factory("command_Configure_low")
    try:
        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        # Invoke TelescopeOn() command on TMC
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        # Invoke AssignResources() Command on TMC
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify transitions after AssignResources command
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        subarray_node_proxy = DeviceProxy(tmc_subarraynode1)
        subarray_node_proxy.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        sdp_subarray = DeviceProxy(sdp_subarray1)
        sdp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

        # Invoking Configure command
        device_params = deepcopy(ON_OFF_DEVICE_COMMAND_DICT)
        device_params["set_wait_for_obsstate"] = False
        result_code, unique_id = tmc_helper.configure_subarray(
            configure_json, **device_params
        )
        assert unique_id[0].endswith("Configure")
        assert result_code[0] == ResultCode.QUEUED

        assertion_data = change_event_callbacks[
            "longRunningCommandResult"
        ].assert_change_event(
            (unique_id[0], Anything),
            lookahead=7,
        )

        assert "Configure" in assertion_data["attribute_value"][0]
        assert (
            "Timeout has occured, command failed"
            in assertion_data["attribute_value"][1]
        )
        assert (
            tmc_sdp_subarray_leaf_node in assertion_data["attribute_value"][1]
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(ResultCode.FAILED.value)),
            lookahead=4,
        )

        sdp_subarray.SetDefective(json.dumps({"enabled": False}))

        # Emulating Csp Subarray going back to READY state after failure
        sdp_subarray.SetDirectObsState(ObsState.READY)

        # Tear Down
        sdp_sln = DeviceProxy(tmc_sdp_subarray_leaf_node)
        sdp_sln.End()

        tear_down(
            release_json, raise_exception=False, **ON_OFF_DEVICE_COMMAND_DICT
        )

    except Exception as e:
        LOGGER.exception("The exception is: %s", e)
        tear_down(
            release_json, raise_exception=True, **ON_OFF_DEVICE_COMMAND_DICT
        )


@pytest.mark.skip(
    reason="AssignResources and ReleaseResources"
    " functionalities are not yet"
    " implemented on mccs master leaf node."
)
@pytest.mark.SKA_low
def test_configure_error_propagation_sdp(json_factory, change_event_callbacks):
    """Verify timeout exception raised when csp set to defective."""
    assign_json = json_factory("command_assign_resource_low")
    release_json = json_factory("command_release_resource_low")
    configure_json = json_factory("command_Configure_low")

    try:
        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        # Invoke TelescopeOn() command on TMC
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        # Invoke AssignResources() Command on TMC
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify transitions after AssignResources command
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        subarray_node_proxy = DeviceProxy(tmc_subarraynode1)
        subarray_node_proxy.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        sdp_subarray = DeviceProxy(sdp_subarray1)
        sdp_subarray.SetDefective(json.dumps(COMMAND_NOT_ALLOWED_DEFECT))

        # Invoking Configure command
        device_params = deepcopy(ON_OFF_DEVICE_COMMAND_DICT)
        device_params["set_wait_for_obsstate"] = False
        result_code, unique_id = tmc_helper.configure_subarray(
            configure_json, **device_params
        )
        assert unique_id[0].endswith("Configure")
        assert result_code[0] == ResultCode.QUEUED

        assertion_data = change_event_callbacks[
            "longRunningCommandResult"
        ].assert_change_event(
            (unique_id[0], Anything),
            lookahead=7,
        )

        assert "Configure" in assertion_data["attribute_value"][0]
        assert (
            "Exception to test exception propagation"
            in assertion_data["attribute_value"][1]
        )
        assert (
            tmc_sdp_subarray_leaf_node in assertion_data["attribute_value"][1]
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(ResultCode.FAILED.value)),
            lookahead=4,
        )

        sdp_subarray.SetDefective(json.dumps({"enabled": False}))
        tear_down(
            release_json, raise_exception=False, **ON_OFF_DEVICE_COMMAND_DICT
        )

    except Exception as e:
        LOGGER.exception("The exception is: %s", e)
        tear_down(
            release_json, raise_exception=True, **ON_OFF_DEVICE_COMMAND_DICT
        )
