"""
TMC Low executes multiple scans with different resources and configurations
"""

import json
from ast import literal_eval

import pytest
from pytest_bdd import parsers, scenario, when
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

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
    check_scan_successful,
)


@pytest.mark.aki
@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp_39894_tmc_sdp_long_sequence.feature",
    "TMC Low executes multiple scans with different "
    "resources and configurations",
)
def test_tmc_sdp_long_sequences():
    """
    TMC Low executes multiple-scan with different resources and configurations
    """


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

    combined_dict = dict(zip(literal_eval(scan_ids), literal_eval(scan_types)))

    for scan_id, scan_type in combined_dict.items():
        configure_json = update_scan_type(configure_json, scan_type)
        _, unique_id = subarray_node_low.store_configuration_data(
            configure_json
        )

        if configure_cycle == "initial":
            assert event_recorder.has_change_event_occurred(
                subarray_node_low.subarray_devices["sdp_subarray"],
                "obsState",
                ObsState.READY,
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


@when(
    parsers.parse(
        "I reassign with new resources to TMC SubarrayNode {subarray_id}"
    )
)
def reassign_resources(
    central_node_low,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node_low,
):
    """A method to move subarray into the IDLE ObsState"""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low_multiple_scan", command_input_factory
    )
    input_json = update_eb_pb_ids(assign_input_json)
    assign_str = json.loads(input_json)
    # Here we are adding this to get an event of ObsState CONFIGURING from
    # SDP Subarray
    assign_str["sdp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2

    _, unique_id = central_node_low.store_resources(json.dumps(assign_str))

    check_subarray_instance(
        subarray_node_low.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(subarray_node_low.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=10,
    )


@when(
    parsers.parse(
        "configure and scan TMC SubarrayNode {subarray_id} "
        "for {new_scan_types} and {new_scan_ids}"
    )
)
def execute_new_configure_scan_sequence(
    subarray_node_low,
    command_input_factory,
    new_scan_ids,
    event_recorder,
    subarray_id,
    new_scan_types,
):
    """A method to invoke configure and scan command"""

    check_subarray_instance(subarray_node_low.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )

    configure_cycle = "initial"
    processed_scan_type = ""

    combined_dict = dict(
        zip(literal_eval(new_scan_ids), literal_eval(new_scan_types))
    )

    for scan_id, scan_type in combined_dict.items():
        configure_json = update_scan_type(configure_json, scan_type)
        _, unique_id = subarray_node_low.store_configuration_data(
            configure_json
        )
        if configure_cycle == "initial":
            assert event_recorder.has_change_event_occurred(
                subarray_node_low.subarray_devices["sdp_subarray"],
                "obsState",
                ObsState.READY,
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
