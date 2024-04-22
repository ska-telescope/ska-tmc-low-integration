"""Test TMC Low executes configure-scan sequence of commands successfully"""

from ast import literal_eval

import pytest
from pytest_bdd import parsers, scenario, when
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_commands,
    update_scan_id,
    update_scan_type,
)
from tests.resources.test_harness.utils.common_utils import (
    check_configure_successful,
    check_scan_successful,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp_39894_tmc_sdp_long_sequence.feature",
    "TMC Low executes configure-scan sequence of commands successfully",
)
def test_tmc_sdp_long_sequences():
    """
    TMC Low executes configure-scan sequence of commands successfully
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
