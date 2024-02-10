"""Test cases for AssignResources and ReleaseResources
 Command for low"""
import json
from copy import deepcopy

import pytest
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DeviceProxy, DevState, EventType

from tests.conftest import LOGGER, TIMEOUT
from tests.resources.test_harness.constant import (
    COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY,
)
from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.common_utils.common_helpers import (
    Resource,
    Waiter,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    TmcHelper,
    tear_down,
)
from tests.resources.test_support.constant_low import (
    DEVICE_HEALTH_STATE_OK_INFO,
    DEVICE_OBS_STATE_IDLE_INFO,
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    INTERMEDIATE_STATE_DEFECT,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    csp_subarray1,
    tmc_csp_subarray_leaf_node,
    tmc_subarraynode1,
)

telescope_control = BaseTelescopeControl()
tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)


@pytest.mark.SKA_low
def test_assign_release_timeout_csp(
    central_node_low,
    event_recorder,
    simulator_factory,
    command_input_factory,
    subarray_node_low,
):
    """Verify timeout exception raised when csp set to defective."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    csp_assign_input_json = prepare_json_args_for_commands(
        "csp_assign_resources", command_input_factory
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
    csp_sim, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    csp_sim.SetDefective(
        json.dumps(COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY)
    )
    result, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED
    exception_message = (
        "Exception occurred on the following devices:"
        + " ska_low/tm_subarray_node/1:"
        + " Exception occurred on the following devices:"
    )
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(unique_id[0], Anything),
    )

    assert "AssignResources" in assertion_data["attribute_value"][0]
    assert exception_message in assertion_data["attribute_value"][1]
    csp_sim.SetDefective(json.dumps({"enabled": False}))
    csp_sim.AssignResources(csp_assign_input_json)
    event_recorder.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.IDLE,
    )


@pytest.mark.pp
@pytest.mark.SKA_low
def test_assign_release_timeout_sdp(
    central_node_low,
    event_recorder,
    simulator_factory,
    command_input_factory,
):
    """Verify timeout exception raised when csp set to defective."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    updated_input_json = json.loads(assign_input_json)
    updated_input_json["sdp"]["execution_block"]["eb_id"] = "eb-xxx"
    updated_input_json = json.dumps(updated_input_json)
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
    _, sdp_sim = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(sdp_sim, "obsState")
    sdp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    result, unique_id = central_node_low.perform_action(
        "AssignResources", updated_input_json
    )
    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED
    exception_message = "Exception occurred on the following devices:"
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(unique_id[0], Anything),
    )
    assert "AssignResources" in assertion_data["attribute_value"][0]
    assert exception_message in assertion_data["attribute_value"][1]


@pytest.mark.unskipped
@pytest.mark.SKA_low
def test_release_exception_propagation(json_factory, change_event_callbacks):
    """Verify timeout exception raised when csp set to defective."""
    assign_json = json_factory("command_assign_resource_low")
    release_json = json_factory("command_release_resource_low")
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

        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)

        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        central_node = DeviceProxy(centralnode)
        central_node.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        csp_subarray = DeviceProxy(csp_subarray1)
        csp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

        device_params = deepcopy(ON_OFF_DEVICE_COMMAND_DICT)
        device_params["set_wait_for_obsstate"] = False
        result, unique_id = tmc_helper.invoke_releaseResources(
            release_json, **device_params
        )

        assert unique_id[0].endswith("ReleaseResources")
        assert result[0] == ResultCode.QUEUED

        exception_message = (
            f"Exception occurred on device: {tmc_subarraynode1}: "
            + "Exception occurred on the following devices:\n"
            + f"{tmc_csp_subarray_leaf_node}: "
            + "Timeout has occurred, command failed\n"
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], exception_message),
            lookahead=4,
        )
        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(ResultCode.FAILED.value)),
            lookahead=4,
        )

        csp_subarray.SetDefective(json.dumps({"enabled": False}))

        # Simulating Csp Subarray going back to IDLE after command failure
        csp_subarray.SetDirectObsState(2)

        # Tear Down
        csp_sln = DeviceProxy(tmc_csp_subarray_leaf_node)
        csp_sln.ReleaseAllResources()

        waiter = Waiter(**ON_OFF_DEVICE_COMMAND_DICT)
        waiter.set_wait_for_going_to_empty()
        waiter.wait(TIMEOUT)
        subarray_node = DeviceProxy(tmc_subarraynode1)
        Resource(subarray_node).assert_attribute("obsState").equals("EMPTY")

        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

    except Exception as e:
        LOGGER.exception("The exception is: %s", e)
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@pytest.mark.SKA_low
def test_health_check_low():
    """Test health state check for low"""
    assert telescope_control.is_in_valid_state(
        DEVICE_HEALTH_STATE_OK_INFO, "healthState"
    )
