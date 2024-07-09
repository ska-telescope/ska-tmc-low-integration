"""Test cases for AssignResources and ReleaseResources
 Command for low"""
import json

import pytest
from assertpy import assert_that
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY,
    TIMEOUT,
    low_sdp_subarray_leaf_node,
)
from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.constant_low import INTERMEDIATE_STATE_DEFECT


@pytest.mark.SKA_low
def test_assign_release_defective_csp(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
):
    """Verify defective exception raised when csp set to defective."""
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
    log_events(
        {
            central_node_low.central_node: ["longRunningCommandResult"],
            central_node_low.subarray_node: ["obsState"],
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
    assert_that(event_tracer).described_as(
        "FAILED INITIAL ASSUMPTION: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )

    csp_sim, _ = get_device_simulators(simulator_factory)
    event_tracer.subscribe_event(csp_sim, "obsState")
    csp_sim.SetDefective(
        json.dumps(COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY)
    )
    result, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED
    exception_message = (
        " ska_low/tm_subarray_node/1:"
        + " Exception occurred on the following devices:"
    )
    log_events({central_node_low.central_node: ["longRunningCommandResult"]})

    result = event_tracer.query_events(
        lambda e: e.has_device(central_node_low.central_node)
        and e.has_attribute("longRunningCommandResult")
        and e.attribute_value[0] == unique_id[0]
        and json.loads(e.attribute_value[1])[0] == ResultCode.FAILED
        and exception_message in json.loads(e.attribute_value[1])[1],
        timeout=TIMEOUT,
    )
    assert_that(result).described_as(
        "FAILED ASSUMPTION ATER ASSIGN RESOURCES: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).is_length(1)

    csp_sim.SetDefective(json.dumps({"enabled": False}))


# timeout is not possible with helper sdp
@pytest.mark.skip("sdp")
@pytest.mark.SKA_low
def test_assign_release_exception_sdp(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """Verify defective exception raised when csp set to defective."""
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    log_events(
        {
            central_node_low.central_node: [
                "longRunningCommandResult",
                "telescopeState",
            ]
        }
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
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
    assert_that(event_tracer).described_as(
        "FAILED INITIAL ASSUMPTION: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )

    assign = json.loads(assign_input_json)
    assign["sdp"]["execution_block"]["eb_id"] = "eb-xxx-218638916"
    assign_input_json = json.dumps(assign)
    result, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED
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
        "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).is_length(1)


@pytest.mark.SKA_low
def test_release_exception_propagation(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
):
    """Verify timeout exception raised when csp set to defective."""
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_low", command_input_factory
    )

    event_tracer.subscribe_event(
        central_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
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
    assert_that(event_tracer).described_as(
        "FAILED INITIAL ASSUMPTION: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    csp_sim, _ = get_device_simulators(simulator_factory)
    event_tracer.subscribe_event(csp_sim, "obsState")

    central_node_low.perform_action("AssignResources", assign_input_json)

    csp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

    assert wait_and_validate_device_attribute_value(
        csp_sim,
        "defective",
        json.dumps(INTERMEDIATE_STATE_DEFECT),
        is_json=True,
    )
    log_events({central_node_low.subarray_node: ["obsState"]})

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
        "Csp Subarray device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.csp_subarray1,
        "obsState",
        ObsState.RESOURCING,
    )
    result, unique_id = central_node_low.perform_action(
        "ReleaseResources", release_input_json
    )
    log_events({central_node_low.central_node: ["longRunningCommandResult"]})
    result = event_tracer.query_events(
        lambda e: e.has_device(central_node_low.central_node)
        and e.has_attribute("longRunningCommandResult")
        and e.attribute_value[0] == unique_id[0]
        and json.loads(e.attribute_value[1])[0] == ResultCode.REJECTED
        and "ReleaseResources command not permitted in observation state 1"
        in json.loads(e.attribute_value[1])[1],
        timeout=TIMEOUT,
    )
    assert_that(result).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "Subarray Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult ResultCode.REJECTED",
    ).is_length(1)


@pytest.mark.SKA_low
def test_assign_release_timeout_csp(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
):
    """Verify command not allowed exception propagation from CSPLeafNodes
    ."""
    csp_subarray_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_CSP_DEVICE
    )

    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
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

    csp_subarray_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    assert wait_and_validate_device_attribute_value(
        csp_subarray_sim,
        "defective",
        json.dumps(INTERMEDIATE_STATE_DEFECT),
        is_json=True,
    )
    _, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    exception_message = "Timeout has occurred, command failed"
    log_events({central_node_low.central_node: ["longRunningCommandResult"]})
    result = event_tracer.query_events(
        lambda e: e.has_device(central_node_low.central_node)
        and e.has_attribute("longRunningCommandResult")
        and e.attribute_value[0] == unique_id[0]
        and json.loads(e.attribute_value[1])[0] == ResultCode.FAILED
        and exception_message in json.loads(e.attribute_value[1])[1],
        timeout=TIMEOUT,
    )
    assert_that(result).described_as(
        "FAILED ASSUMPTION ATER ASSIGN RESOURCES: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).is_length(1)
