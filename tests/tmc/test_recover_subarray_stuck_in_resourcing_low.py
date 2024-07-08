"""Test cases for recovery of subarray stuck in RESOURCING
ObsState for low"""
import json

import pytest
from assertpy import assert_that
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import low_sdp_subarray_leaf_node
from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.constant_low import (
    FAILED_RESULT_DEFECT,
    TIMEOUT,
)


@pytest.mark.SKA_low
def test_recover_subarray_stuck_in_resourcing_low(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
):
    """AssignResources and ReleaseResources is executed."""
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    log_events(
        {
            central_node_low.central_node: ["longRunningCommandResult"],
            central_node_low.subarray_node: ["obsState"],
            central_node_low.subarray_devices["csp_subarray"]: ["obsState"],
            central_node_low.subarray_devices["sdp_subarray"]: ["obsState"],
            central_node_low.subarray_devices["mccs_subarray"]: ["obsState"],
        }
    )
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )

    csp_sim, sdp_sim = get_device_simulators(simulator_factory)
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    assign = json.loads(assign_input_json)
    assign["sdp"]["execution_block"]["eb_id"] = "eb-xxx-218638916"
    assign_input_json = json.dumps(assign)
    _, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    exception_message = (
        "Exception occurred on the following devices: "
        f"{low_sdp_subarray_leaf_node}:"
        " Invalid eb_id in the AssignResources input json"
    )
    result = event_tracer.query_events(
        lambda e: e.has_device(central_node_low.central_node)
        and e.has_attribute("longRunningCommandResult")
        and e.attribute_value[0] == unique_id[0]
        and json.loads(e.attribute_value[1])[0] == ResultCode.FAILED
        and exception_message in json.loads(e.attribute_value[1])[1],
        timeout=TIMEOUT,
    )

    assert_that(result).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).is_length(1)

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "SDP Subarray device"
        f"({central_node_low.subarray_devices['sdp_subarray'].dev_name()})"
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.RESOURCING,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "CSP Subarray device"
        f"({csp_sim.dev_name()})"
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "CSP Subarray device"
        f"({mccs_sim.dev_name()})"
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.IDLE,
    )

    sdp_sim.SetDefective(json.dumps({"enabled": False}))
    sdp_sim.SetDirectObsState(ObsState.EMPTY)
    csp_sim.ReleaseAllResources()
    mccs_sim.ReleaseAllResources()

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
        "SDP Subarray device"
        f"({central_node_low.subarray_devices['sdp_subarray'].dev_name()})"
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
        "CSP Subarray device"
        f"({csp_sim.dev_name()})"
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
        "MCCS Subarray device"
        f"({mccs_sim.dev_name()})"
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@pytest.mark.SKA_low
@pytest.mark.parametrize("defective_device", ["csp_subarray", "sdp_subarray"])
def test_abort_with_sdp_csp_in_empty(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
    defective_device: str,
):
    """recover subarray when SDP and CSP is in empty with abort."""
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_low.subarray_node: ["obsState"],
            central_node_low.subarray_devices["sdp_subarray"]: ["obsState"],
            central_node_low.subarray_devices["mccs_subarray"]: ["obsState"],
        }
    )
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    csp_sim, sdp_sim = get_device_simulators(simulator_factory)
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    defective_device_proxy = central_node_low.subarray_devices.get(
        defective_device
    )
    # Set SDP and CSP into FAILED RESULT to change from RESOURCING to EMPTY
    if defective_device != "sdp_subarray":
        failed_result_defect = FAILED_RESULT_DEFECT
        failed_result_defect["target_obsstates"] = [
            ObsState.RESOURCING,
            ObsState.EMPTY,
        ]

        defective_device_proxy.SetDefective(json.dumps(failed_result_defect))

        assert wait_and_validate_device_attribute_value(
            defective_device_proxy,
            "defective",
            json.dumps(failed_result_defect),
            is_json=True,
        )
    else:
        assign = json.loads(assign_input_json)
        assign["sdp"]["resources"]["receive_nodes"] = 0
        assign_input_json = json.dumps(assign)

    _, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )

    exception_message = (
        "Exception occurred on the following devices: "
        f"ska_low/tm_leaf_node/{defective_device}01: "
    )

    result = event_tracer.query_events(
        lambda e: e.has_device(central_node_low.central_node)
        and e.has_attribute("longRunningCommandResult")
        and e.attribute_value[0] == unique_id[0]
        and json.loads(e.attribute_value[1])[0] == ResultCode.FAILED
        and exception_message in json.loads(e.attribute_value[1])[1],
        timeout=TIMEOUT,
    )

    assert_that(result).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).is_length(1)
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "Subarray device"
        f"({defective_device_proxy.dev_name()})"
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        defective_device_proxy,
        "obsState",
        ObsState.RESOURCING,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "Subarray device"
        f"({defective_device_proxy.dev_name()})"
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        defective_device_proxy,
        "obsState",
        ObsState.EMPTY,
    )

    if defective_device_proxy.dev_name() != csp_sim.dev_name():
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
            "CSP Subarray device"
            f"({csp_sim.dev_name()})"
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            csp_sim,
            "obsState",
            ObsState.IDLE,
        )
    elif defective_device_proxy.dev_name() != sdp_sim.dev_name():
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
            "SDP Subarray device"
            f"({sdp_sim.dev_name()})"
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            sdp_sim,
            "obsState",
            ObsState.IDLE,
        )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "MCCS Subarray device"
        f"({mccs_sim.dev_name()})"
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.IDLE,
    )

    defective_device_proxy.SetDefective(json.dumps({"enabled": False}))

    central_node_low.subarray_node.Abort()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in ABORTED obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@pytest.mark.SKA_low
def test_abort_with_mccs_in_empty(
    subarray_node_low: SubarrayNodeWrapperLow,
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
):
    """recover subarray when MCCS is in empty with abort."""
    csp_sim, sdp_sim = get_device_simulators(simulator_factory)
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )

    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(csp_sim, "obsState")
    event_tracer.subscribe_event(sdp_sim, "obsState")
    event_tracer.subscribe_event(mccs_sim, "obsState")
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_low.subarray_node: ["obsState"],
            csp_sim: ["obsState"],
            mccs_sim: ["obsState"],
            sdp_sim: ["obsState"],
        }
    )
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )

    # Set MCCS into FAILED RESULT to change from RESOURCING to EMPTY
    failed_result_defect = FAILED_RESULT_DEFECT
    failed_result_defect["target_obsstates"] = [
        ObsState.RESOURCING,
        ObsState.EMPTY,
    ]

    mccs_sim.SetDefective(json.dumps(failed_result_defect))

    assert wait_and_validate_device_attribute_value(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "defective",
        json.dumps(failed_result_defect),
        is_json=True,
    )
    _, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )

    exception_message = (
        " ska_low/tm_subarray_node/1: "
        + "Timeout has occurred, command failed"
    )

    result = event_tracer.query_events(
        lambda e: e.has_device(central_node_low.central_node)
        and e.has_attribute("longRunningCommandResult")
        and e.attribute_value[0] == unique_id[0]
        and json.loads(e.attribute_value[1])[0] == ResultCode.FAILED
        and exception_message in json.loads(e.attribute_value[1])[1],
        timeout=TIMEOUT,
    )

    assert_that(result).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).is_length(1)

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "MCCS Subarray device"
        f"({mccs_sim.dev_name()})"
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.RESOURCING,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "SDP Subarray device"
        f"({sdp_sim.dev_name()})"
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.IDLE,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "CSP Subarray device"
        f"({csp_sim.dev_name()})"
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
        "MCCS Subarray device"
        f"({mccs_sim.dev_name()})"
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.EMPTY,
    )

    mccs_sim.SetDefective(json.dumps({"enabled": False}))
    assert wait_and_validate_device_attribute_value(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "defective",
        json.dumps({"enabled": False}),
        is_json=True,
    )
    subarray_node_low.subarray_node.Abort()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "CSP Subarray device"
        f"({csp_sim.dev_name()}) "
        "is expected to be in ABORTED obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.ABORTED,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "SDP Subarray device"
        f"({sdp_sim.dev_name()}) "
        "is expected to be in ABORTED obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.ABORTED,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in ABORTED obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
