"""Test module for TMC-SDP Json error propagation functionality """


import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    get_assign_json_id,
    get_device_simulator_with_given_name,
    update_eb_pb_ids,
)
from tests.resources.test_harness.utils.enums import ResultCode


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp_34886_sdp_json_error_duplicate_id.feature",
    "TMC Subarray report the exception triggered by the SDP subarray "
    + "when it encounters a duplicate eb-id/pb-id.",
)
def test_tmc_sdp_json_error_duplicate_id():
    """
    Test case to verify TMC-SDP json error propagation
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("a Telescope consisting of TMC, SDP, simulated CSP and simulated MCCS")
def given_a_tmc_sdp(
    central_node_low: CentralNodeWrapperLow, simulator_factory
):
    """Method to check TMC real devices and sub-system simulators

    Args:
        central_node_low (CentralNodeWrapperLow): fixture for a
        TMC CentralNode under test
        simulator_factory (_type_):fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    simulated_devices = get_device_simulator_with_given_name(
        simulator_factory, ["csp master", "mccs master", "mccs subarray"]
    )
    if len(simulated_devices) == 3:
        csp_master_sim = simulated_devices[0]
        mccs_master_sim = simulated_devices[1]
        mccs_subarray_sim = simulated_devices[2]
        assert csp_master_sim.ping() > 0
        assert mccs_master_sim.ping() > 0
        assert mccs_subarray_sim.ping() > 0
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0


@given(
    parsers.parse(
        "The TMC and SDP subarray {subarray_id} in the IDLE "
        + "obsState using {input_json1}"
    )
)
def check_tmc_sdp_subarray_idle(
    subarray_id: str,
    input_json1: str,
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Method to verify resources are assigned successfully.
    Checks TMC Subarray and SDP Subarray is in obsstate IDLE

    Args:
        subarray_id (str): subarray id used for testing
        input_json1 (str): assign resources input json
        central_node_low (CentralNodeWrapperLow): fixture for
        CentralNodeWrapperLow class instance
        event_recorder (EventRecorder):fixture for EventRecorder class instance
    """
    central_node_low.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        central_node_low.get_subarray_devices_by_id(subarray_id).get(
            "sdp_subarray_leaf_node"
        ),
        "longRunningCommandResult",
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.get_subarray_devices_by_id(subarray_id).get(
            "sdp_subarray"
        ),
        "obsState",
    )

    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )

    assign_input = (
        central_node_low.json_factory.create_centralnode_configuration(
            input_json1
        )
    )
    central_node_low.assign_input = assign_input
    central_node_low.store_resources(assign_input)

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(
    parsers.parse(
        "TMC executes another AssignResources command "
        + "with a {duplicate_id} from {input_json1}"
    )
)
def tmc_assign_resources_with_duplicate_id(
    duplicate_id: str,
    input_json1: str,
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Method to assign resources again with
    duplicate id for SDP Subarray configuration

    Args:
        duplicate_id (str): Type ID to be duplicated(eb_id/pb_id).
        input_json1 (str): assign resources input json
        central_node_low (CentralNodeWrapperLow): fixture for
        CentralNodeWrapperLow class instance
        event_recorder (EventRecorder):
    """
    event_recorder.subscribe_event(
        central_node_low.sdp_subarray_leaf_node,
        "longRunningCommandResult",
    )
    json_id: str = ""
    if duplicate_id == "eb_id":
        json_id = "pb_id"
    else:
        json_id = "eb_id"
    assign_input = (
        central_node_low.json_factory.create_centralnode_configuration(
            input_json1
        )
    )
    assign_input = update_eb_pb_ids(
        central_node_low.assign_input, json_id=json_id
    )
    pytest.result, pytest.unique_id = central_node_low.perform_action(
        "AssignResources", assign_input
    )
    assert pytest.unique_id[0].endswith("AssignResources")
    assert pytest.result[0] == ResultCode.QUEUED
    pytest.duplicate_id_type = duplicate_id
    pytest.duplicate_id = get_assign_json_id(assign_input, duplicate_id)[0]


@when(
    parsers.parse(
        "SDP subarray {subarray_id} throws an exception "
        + "and remain in IDLE obsState"
    )
)
def check_sdp_error(
    subarray_id: str,
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Method to verify SDP Subarray raises exception
    with duplicate id in SDP configuration.
    Checks SDP Subarray remains in obsstate IDLE

    Args:
        subarray_id (str): subarray id used for testing
        central_node_low (CentralNodeWrapperLow): fixture for
        CentralNodeWrapperLow class instance
        event_recorder (EventRecorder):fixture for EventRecorder class instance
    """
    sdp_subarray = central_node_low.get_subarray_devices_by_id(
        subarray_id
    ).get("sdp_subarray")
    sdp_subarray_leaf_node = central_node_low.get_subarray_devices_by_id(
        subarray_id
    ).get("sdp_subarray_leaf_node")
    sdp_subarray_obsstate = sdp_subarray.obsState

    assert sdp_subarray_obsstate == ObsState.IDLE
    if pytest.duplicate_id_type == "pb_id":
        exception_message = (
            f"Processing block {pytest.duplicate_id} already exists"
        )
    else:
        exception_message = (
            f"Execution block {pytest.duplicate_id} already exists"
        )
    assertion_data = event_recorder.has_change_event_occurred(
        sdp_subarray_leaf_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(Anything, Anything),
    )
    assert exception_message in assertion_data["attribute_value"][1]


@when(
    parsers.parse("TMC subarray {subarray_id} remain in RESOURCING obsState")
)
def check_tmc_resourcing_obstate(
    subarray_id: str,
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """
    Method to verify TMC Subarray stucks in obsstate RESOURCING
    once SDP Subarray raises exception

    Args:
        subarray_id (str): subarray id used for testing
        central_node_low (CentralNodeWrapperLow): fixture for
        CentralNodeWrapperLow class instance
        event_recorder (EventRecorder):fixture for EventRecorder class instance
    """
    assert event_recorder.has_change_event_occurred(
        central_node_low.get_subarray_devices_by_id(subarray_id).get(
            "subarray_node"
        ),
        "obsState",
        ObsState.RESOURCING,
    )


@then("exception is propagated to central node")
def check_central_node_exception_propagation(
    central_node_low: CentralNodeWrapperLow, event_recorder: EventRecorder
):
    """Method to verify exception raised by SDP Subarray
    is prapogated to TMC nodes

    Args:
        central_node_low (CentralNodeWrapperLow): fixture for
        CentralNodeWrapperLow class instance
        event_recorder (EventRecorder):fixture for EventRecorder class instance
    """
    if pytest.duplicate_id_type == "pb_id":
        exception_message = (
            f"Processing block {pytest.duplicate_id} already exists"
        )
    else:
        exception_message = (
            f"Execution block {pytest.duplicate_id} already exists"
        )
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(pytest.unique_id[0], Anything),
    )
    assert exception_message in assertion_data["attribute_value"][1]
