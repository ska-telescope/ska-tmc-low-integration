"""
This module defines a Pytest BDD test scenario for checking the rejection of
invalid JSON inputs during the Configure command execution on a
Telescope Monitoring and Control (TMC) system
The scenario includes steps to set up the TMC, configure the subarray,
and validate the rejection
of various invalid JSON inputs.
"""
import json
from copy import deepcopy

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from tests.conftest import LOGGER
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    TmcHelper,
    prepare_json_args_for_centralnode_commands,
    tear_down,
)
from tests.resources.test_support.constant_low import (
    DEVICE_OBS_STATE_EMPTY_INFO,
    DEVICE_OBS_STATE_IDLE_INFO,
    DEVICE_OBS_STATE_READY_INFO,
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
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
@scenario(
    "../features/tmc/check_invalid_json_not_allowed.feature",
    "Invalid json rejected by TMC Low for Configure command",
)
def test_invalid_json_in_configure_obsState():
    """
    Test SubarrayNode Low Configure command with invalid json data.
    """


@given("the TMC is On")
def given_tmc(command_input_factory, central_node_low):
    """Ensure the TMC is in the 'On' state."""
    release_json = prepare_json_args_for_centralnode_commands(
        "command_release_resource_low", command_input_factory
    )
    try:
        # Verify Telescope is Off/Standby
        assert central_node_low.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        # Invoke TelescopeOn() command on TMC CentralNode
        LOGGER.info("Invoking TelescopeOn command on TMC CentralNode")
        central_node_low.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeOn
        assert central_node_low.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@given("the subarray is in IDLE obsState")
def tmc_check_status(central_node_low, command_input_factory):
    """Set the subarray to 'IDLE' observation state."""
    assert central_node_low.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "State"
    )
    assign_json = prepare_json_args_for_centralnode_commands(
        "command_assign_resources_low", command_input_factory
    )
    LOGGER.info("Invoking AssignResources command on TMC CentralNode")
    central_node_low.store_resources(assign_json)

    # Verify ObsState is IDLE
    assert central_node_low.is_in_valid_state(
        DEVICE_OBS_STATE_IDLE_INFO, "State"
    )


@when(
    parsers.parse("the command Configure is invoked with {invalid_json} input")
)
def send(json_factory, invalid_json, command_input_factory):
    """Invoke the Configure command with different invalid JSON inputs."""
    device_params = deepcopy(ON_OFF_DEVICE_COMMAND_DICT)
    device_params["set_wait_for_obsstate"] = False
    release_json = json_factory("command_release_resource_low")
    try:
        configure_json = prepare_json_args_for_centralnode_commands(
            "command_assign_resources_low", command_input_factory
        )
        if invalid_json == "csp_key_missing":
            invalid_configure_json = json.loads(configure_json)
            del invalid_configure_json["csp"]
            pytest.command_result = tmc_helper.configure_subarray(
                json.dumps(invalid_configure_json), **device_params
            )
        elif invalid_json == "sdp_key_missing":
            invalid_configure_json = json.loads(configure_json)
            del invalid_configure_json["sdp"]
            pytest.command_result = tmc_helper.configure_subarray(
                json.dumps(invalid_configure_json), **device_params
            )
        elif invalid_json == "tmc_key_missing":
            invalid_configure_json = json.loads(configure_json)
            del invalid_configure_json["tmc"]
            pytest.command_result = tmc_helper.configure_subarray(
                json.dumps(invalid_configure_json), **device_params
            )
        elif invalid_json == "scan_duration_key_missing":
            invalid_configure_json = json.loads(configure_json)
            del invalid_configure_json["tmc"]["scan_duration"]
            pytest.command_result = tmc_helper.configure_subarray(
                json.dumps(invalid_configure_json), **device_params
            )
        elif invalid_json == "empty_string":
            invalid_configure_json = ""
            pytest.command_result = tmc_helper.configure_subarray(
                invalid_configure_json, **device_params
            )
    except Exception as e:
        LOGGER.exception(f"Exception occurred: {e}")
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@then(
    parsers.parse(
        "the TMC should reject the {invalid_json} with ResultCode.Rejected"
    )
)
def invalid_command_rejection(invalid_json):
    """Verify that the TMC rejects the invalid JSON with the expected
    ResultCode  and validation messages."""
    # asserting validation resultcode
    assert pytest.command_result[0][0] == ResultCode.REJECTED
    # asserting validations message as per invalid json
    if invalid_json == "csp_key_missing":
        assert (
            "Malformed input string. The key: `csp` is missing."
            in pytest.command_result[1][0]
        )
    elif invalid_json == "sdp_key_missing":
        assert (
            "Malformed input string. The key: `sdp` is missing."
            in pytest.command_result[1][0]
        )
    elif invalid_json == "tmc_key_missing":
        assert (
            "Malformed input string. The key: `tmc` is missing."
            in pytest.command_result[1][0]
        )
    elif invalid_json == "scan_duration_key_missing":
        assert (
            "Malformed input string. The key -> `scan_duration` is missing"
            in pytest.command_result[1][0]
        )
    elif invalid_json == "empty_string":
        assert "Malformed input string" in pytest.command_result[1][0]


@then("TMC subarray remains in IDLE obsState")
def tmc_status(central_node_low):
    """Ensure that the TMC subarray remains in the 'IDLE' observation state
    after rejection."""
    # Verify obsState transitions
    assert central_node_low.is_in_valid_state(
        DEVICE_OBS_STATE_IDLE_INFO, "obsState"
    )


@then(
    "TMC successfully executes the Configure \
command for the subarray with a valid json"
)
def tmc_accepts_next_commands(central_node_low, command_input_factory):
    """Execute the Configure command with a valid JSON and verify successful
    execution."""
    release_json = prepare_json_args_for_centralnode_commands(
        "command_release_resource_low", command_input_factory
    )
    try:
        configure_json = prepare_json_args_for_centralnode_commands(
            "command_Configure_low", command_input_factory
        )
        LOGGER.info(f"Input argin for Configure: {configure_json}")

        # Invoke Configure() Command on TMC
        LOGGER.info("Invoking Configure command on TMC SubarrayNode")
        central_node_low.perform_action("configure", configure_json)
        assert central_node_low.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )
        assert central_node_low.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "State"
        )

        # teardown
        LOGGER.info("Invoking END on TMC")
        tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)

        #  Verify obsState is IDLE
        assert central_node_low.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        LOGGER.info("Invoking ReleaseResources on TMC")
        central_node_low.invoke_release_resources(release_json)

        assert central_node_low.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        LOGGER.info("Invoking Telescope Standby on TMC")
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)

        assert central_node_low.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Tear Down complete. Telescope is in Standby State")
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
