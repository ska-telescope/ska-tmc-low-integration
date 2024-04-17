"""Test TMC Low executes configure-scan sequence of commands successfully"""
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_eb_pb_ids,
    update_scan_id,
    update_scan_type,
)
from tests.resources.test_harness.utils.common_utils import (
    check_configure_successful,
    check_obsstate_sdp_in_first_configure,
    check_scan_successful,
)


@pytest.mark.aki
@pytest.mark.tmc_sdp1
@scenario(
    "../features/tmc_sdp/xtp_xxxxx_tmc_sdp_long_sequence.feature",
    "TMC Low executes configure-scan sequence of commands successfully",
)
def test_tmc_sdp_long_sequences():
    """
    TMC Low executes configure-scan sequence of commands successfully
    """


@given("the Telescope is in ON state")
def telescope_is_in_on_state(central_node_low, event_recorder):
    """Move the telescope to the ON state and verify the state change.

    Args:
        central_node_low (CentralNodeLow): An instance of the CentralNodeLow
        class representing the central node.
        event_recorder (EventRecorder): An instance of the EventRecorder class
        for recording events.

    """
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@when(parsers.parse("I assign resources to TMC SubarrayNode {subarray_id}"))
def assign_resources_to_subarray(
    central_node_low, subarray_node_low, command_input_factory, event_recorder
):
    """Method to assign resources to subarray."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "scanType"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "scanID"
    )
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low_multiple_scan", command_input_factory
    )
    input_json = update_eb_pb_ids(input_json)
    _, unique_id = central_node_low.store_resources(input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(ResultCode.OK.value)),
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


time.sleep(3)


# @when(
#     parsers.parse(
#         "configure and scan TMC SubarrayNode {subarray_id} "
#         "for each {scan_types} and {scan_ids}"
#     )
# )
# def execute_configure_scan_sequence(
#     subarray_node_low,
#     event_recorder,
#     command_input_factory,
#     scan_types,
#     scan_ids,
#     subarray_id,
# ):
#     """A method to invoke Configure command"""
#     event_recorder.subscribe_event(
#         subarray_node_low.subarray_node, "longRunningCommandResult"
#     )
#     input_json = prepare_json_args_for_commands(
#         "configure_low", command_input_factory
#     )
#     input_json = json.loads(input_json)
#     input_json["sdp"]["scan_type"] = scan_types
#     _, unique_id = subarray_node_low.store_configuration_data(
#         input_json=json.dumps(input_json)
#     )
#     assert event_recorder.has_change_event_occurred(
#         subarray_node_low.subarray_node,
#         "longRunningCommandResult",
#         (unique_id[0], str(ResultCode.OK.value)),
#     )
#     event_recorder.subscribe_event(
#         subarray_node_low.subarray_devices["sdp_subarray"], "obsState"
#     )

#     assert event_recorder.has_change_event_occurred(
#         subarray_node_low.subarray_devices["sdp_subarray"],
#         "obsState",
#         ObsState.READY,
#     )

#     input_json_scan = prepare_json_args_for_commands(
#         "scan_low", command_input_factory
#     )
#     scan_json = json.loads(input_json_scan)
#     scan_json["scan_id"] = int(scan_ids)

#     subarray_node_low.set_subarray_id(subarray_id)
#     subarray_node_low.store_scan_data(json.dumps(scan_json))
#     event_recorder.subscribe_event(
#         subarray_node_low.subarray_devices["sdp_subarray"], "scanID"
#     )
#     assert event_recorder.has_change_event_occurred(
#         subarray_node_low.subarray_devices["sdp_subarray"],
#         "scanID",
#         int(scan_ids),
#     )

#     assert event_recorder.has_change_event_occurred(
#         subarray_node_low.subarray_node,
#         "obsState",
#         ObsState.SCANNING,
#     )
#     assert event_recorder.has_change_event_occurred(
#         subarray_node_low.subarray_devices["sdp_subarray"],
#         "obsState",
#         ObsState.SCANNING,
#     )
#     subarray_node_low.remove_scan_data()
#     # wait for scan duration to get over
#     assert event_recorder.has_change_event_occurred(
#         subarray_node_low.subarray_devices["sdp_subarray"],
#         "obsState",
#         ObsState.READY,
#     )

# pylint: disable=eval-used
@when(
    parsers.parse(
        "configure and scan TMC SubarrayNode {subarray_id} for "
        "each {scan_types} and {scan_ids}"
    )
)
def execute_configure_scan_sequence(
    subarray_node_low,
    command_input_factory,
    scan_ids,
    event_recorder,
    subarray_id,
    scan_types,
):
    """A method to invoke configure and scan  command"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    check_subarray_instance(subarray_node_low.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )

    configure_cycle = "initial"
    processed_scan_type = ""

    combined_dict = dict(zip(eval(scan_ids), eval(scan_types)))

    for scan_id, scan_type in combined_dict.items():
        configure_json = update_scan_type(configure_json, scan_type)
        _, unique_id = subarray_node_low.store_configuration_data(
            configure_json
        )

        if configure_cycle == "initial":
            check_obsstate_sdp_in_first_configure(
                event_recorder, subarray_node_low
            )
            configure_cycle = "Next"

        check_configure_successful(
            subarray_node_low,
            event_recorder,
            unique_id,
            scan_type,
            processed_scan_type,
        )

        scan_json = prepare_json_args_for_commands(
            "scan_low", command_input_factory
        )
        scan_json = update_scan_id(scan_json, scan_id)
        _, unique_id = subarray_node_low.execute_transition(
            "Scan", argin=scan_json
        )
        check_scan_successful(
            subarray_node_low, event_recorder, scan_id, unique_id
        )
        processed_scan_type = scan_type


@when(parsers.parse("end the configuration on TMC SubarrayNode {subarray_id}"))
def invoke_end(subarray_node_low, event_recorder):
    """A method to invoke End command"""
    _, unique_id = subarray_node_low.end_observation()
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(ResultCode.OK.value)),
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@when(parsers.parse("release the resources on TMC SubarrayNode {subarray_id}"))
def release_resources_to_subarray(
    central_node_low, command_input_factory, event_recorder
):
    """Method to release resources to subarray."""
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.invoke_release_resources(
        release_input_json
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(ResultCode.OK.value)),
    )


@then("TMC SubarrayNode transitions to EMPTY ObsState")
def check_tmc_is_in_empty_obsstate(central_node_low, event_recorder):
    """Method to check TMC is is in EMPTY obsstate."""
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    assert central_node_low.subarray_devices["sdp_subarray"].Resources == "{}"
