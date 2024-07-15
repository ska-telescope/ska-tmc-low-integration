"""Test module to test TMC-CSP Configure functionality."""
import json
import logging

import pytest
import tango
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_support.common_utils.result_code import ResultCode

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_csp1
@scenario(
    "../features/tmc_csp/xtp-29854_configure.feature",
    "Configure CSP subarray using TMC",
)
def test_tmc_csp_configure_functionality(central_node_low) -> None:
    """
    Test case to verify TMC-CSP Configure functionality
    """

    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["csp_subarray"].ping() > 0


@given("the Telescope is in ON state")
def check_telescope_is_in_on_state(
    central_node_real_csp_low, event_recorder
) -> None:
    """Ensure telescope is in ON state."""
    central_node_real_csp_low.csp_master.adminMode = 0
    central_node_real_csp_low.csp_subarray1.adminMode = 0
    LOGGER.info(
        "My adminmode is1 %s", central_node_real_csp_low.csp_master.adminMode
    )
    LOGGER.info(
        "My adminmode is2  %s",
        central_node_real_csp_low.csp_subarray1.adminMode,
    )
    pst = tango.DeviceProxy("low-pst/beam/01")
    wait_and_validate_device_attribute_value(pst, "State", "DevState.ON")
    LOGGER.info("My adminmode is3  %s", pst.adminMode)

    central_node_real_csp_low.move_to_on()
    LOGGER.info("My devstate is is3 %s", pst.state())
    event_recorder.subscribe_event(
        central_node_real_csp_low.central_node, "telescopeState"
    )
    # pst = tango.DeviceProxy("low-pst/beam/01")
    # time.sleep(2)
    # assert "ON" in pst.State()
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("the subarray {subarray_id} obsState is IDLE"))
def move_subarray_node_to_idle_obsstate(
    central_node_real_csp_low,
    event_recorder,
    command_input_factory,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to IDLE obsstate."""
    central_node_real_csp_low.set_subarray_id(subarray_id)
    receive_address = json.dumps(
        {
            "science_A": {
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.1"]],
                "port": [[0, 9000, 1], [2000, 9000, 1]],
            },
            "target:a": {
                "vis0": {
                    "function": "visibilities",
                    "visibility_beam_id": 1,
                    "host": [
                        [0, "192.168.0.1"],
                    ],
                    "port": [
                        [0, 9000, 1],
                    ],
                    "mac": [
                        [0, "06-00-00-00-00-00"],
                    ],
                }
            },
            "calibration:b": {
                "vis0": {
                    "function": "visibilities",
                    "host": [
                        [0, "192.168.0.1"],
                        [400, "192.168.0.2"],
                        [744, "192.168.0.3"],
                        [1144, "192.168.0.4"],
                    ],
                    "port": [
                        [0, 9000, 1],
                        [400, 9000, 1],
                        [744, 9000, 1],
                        [1144, 9000, 1],
                    ],
                    "mac": [
                        [0, "06-00-00-00-00-00"],
                        [744, "06-00-00-00-00-01"],
                    ],
                }
            },
        }
    )
    central_node_real_csp_low.subarray_devices[
        "sdp_subarray"
    ].SetDirectreceiveAddresses(receive_address)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    event_recorder.subscribe_event(
        central_node_real_csp_low.subarray_node, "obsState"
    )
    event_recorder.subscribe_event(
        central_node_real_csp_low.central_node, "longRunningCommandResult"
    )
    central_node_real_csp_low.set_serial_number_of_cbf_processor()
    _, unique_id = central_node_real_csp_low.store_resources(assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.has_change_event_occurred(
        central_node_real_csp_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@when("I configure the subarray")
def invoke_configure_command(
    subarray_node_real_csp_low, command_input_factory, event_recorder
) -> None:
    """Invoke Configure command."""
    event_recorder.subscribe_event(
        subarray_node_real_csp_low.subarray_node, "longRunningCommandResult"
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, unique_id = subarray_node_real_csp_low.store_configuration_data(
        configure_input_json
    )
    event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@then("the CSP subarray transitions to READY obsState")
def check_if_csp_subarray_moved_to_ready_obsstate(
    subarray_node_real_csp_low, event_recorder
) -> None:
    """Ensure CSP subarray is moved to READY obsstate"""
    event_recorder.subscribe_event(
        subarray_node_real_csp_low.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then("the TMC subarray transitions to READY obsState")
def check_if_tmc_subarray_moved_to_ready_obsstate(
    subarray_node_real_csp_low, event_recorder
) -> None:
    """Ensure TMC Subarray is moved to READY obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
