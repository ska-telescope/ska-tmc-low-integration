"""Test module for TMC-SDP Json error propagation functionality """
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    get_device_simulator_with_given_name,
    update_eb_pb_ids,
)
from tests.resources.test_harness.utils.enums import ResultCode


@pytest.mark.tmc_sdp1
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


@given("a Telescope consisting of TMC,SDP,simulated CSP and simulated MCCS")
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
    csp_master_sim, mccs_master_sim, mccs_subarray_sim = simulated_devices
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0
    assert csp_master_sim.ping() > 0
    assert mccs_master_sim.ping() > 0
    assert mccs_subarray_sim.ping() > 0


@given(
    parsers.parse(
        "The TMC and SDP subarray {subarray_id} in the IDLE "
        + "obsState using {input_json1}"
    )
)
def check_tmc_sdp_subarray_idle(
    subarray_id: str,
    input_json1: str,
    json_factory,
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Method to verify resources are assigned successfully.
    Checks TMC Subarray and SDP Subarray is in obsstate IDLE

    Args:
        subarray_id (str): _description_
        input_json1 (str): _description_
        json_factory (_type_): _description_
        central_node_low (CentralNodeWrapperLow): _description_
        event_recorder (EventRecorder): _description_
    """

    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices.get("sdp_subarray"), "obsState"
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
):
    """Method to assign resources again with
    duplicate id for SDP Subarray configuration

    Args:
        duplicate_id (str): _description_
        input_json1 (str): _description_
        central_node_low (CentralNodeWrapperLow): _description_
    """
    if duplicate_id == "eb_id":
        id = "pb_id"
    else:
        id = "eb_id"
    assign_input = update_eb_pb_ids(central_node_low.assign_input, id=id)
    assign_input = (
        central_node_low.json_factory.create_centralnode_configuration(
            input_json1
        )
    )
    pytest.result, pytest.unique_id = central_node_low.store_resources(
        assign_input
    )
    assert pytest.unique_id[0].endswith("AssignResources")
    assert pytest.result[0] == ResultCode.QUEUED


@when(
    parsers.parse(
        "SDP subarray {subarray_id} throws an exception"
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
        subarray_id (str): _description_
        central_node_low (CentralNodeWrapperLow): _description_
        event_recorder (EventRecorder): _description_
    """
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )


@when(
    parsers.parse(
        "TMC subarray {subarray_id} " + "remain in RESOURCING obsState"
    )
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
        subarray_id (str): _description_
        central_node_low (CentralNodeWrapperLow): _description_
        event_recorder (EventRecorder): _description_
    """
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
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
        central_node_low (CentralNodeWrapperLow): _description_
        event_recorder (EventRecorder): _description_
    """
    exception_message = (
        "Exception occurred on the following devices:"
        + " ska_low/tm_subarray_node/1:"
        + " Exception occurred on the following devices:"
    )
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(pytest.unique_id[0], Anything),
    )
    assert exception_message in assertion_data["attribute_value"][1]


@when(parsers.parse("I issue the Abort command on TMC Subarray {subarray_id}"))
def abort_tmc_subarray(
    subarray_id: str, central_node_low: CentralNodeWrapperLow
):
    """Method to invoke Abort command from TMC Subarray

    Args:
        subarray_id (str): _description_
        central_node_low (CentralNodeWrapperLow): _description_
    """
    central_node_low.subarray_abort()


@when(
    parsers.parse(
        "SDP Subarray and TMC Subarray {subarray_id} "
        + "transitions to obsState ABORTED"
    )
)
def check_tmc_sdp_subarray_aborted_obstate(
    subarray_id: str,
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Verify TMC Subarray and SDP Subarray is
    in obsstate ABORTED after Abort is successful

    Args:
        subarray_id (str): _description_
        central_node_low (CentralNodeWrapperLow): _description_
        event_recorder (EventRecorder): _description_
    """

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
    parsers.parse("I issue the Restart command on TMC Subarray {subarray_id>}")
)
def restart_tmc_subarray(
    subarray_id: str, central_node_low: CentralNodeWrapperLow
):
    """Method to invoke Restart command from TMC Subarray

    Args:
        subarray_id (str): _description_
        central_node_low (CentralNodeWrapperLow): _description_
    """
    central_node_low.subarray_restart()


@when(
    parsers.parse(
        "the SDP and TMC Subarray {subarray_id} transitions to obsState EMPTY"
    )
)
def check_tmc_sdp_empy_obstate(
    subarray_id: str,
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Verify TMC Subarray and SDP Subarray is
    in obsstate EMPTY after Restart is successful

    Args:
        subarray_id (str): _description_
        central_node_low (CentralNodeWrapperLow): _description_
        event_recorder (EventRecorder): _description_
    """
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


@then(
    parsers.parse(
        "AssignResources command is executed with a "
        + "new ID and TMC and SDP subarray {subarray_id} transitions to IDLE"
    )
)
def assign_resources_with_new_id(
    subarray_id: str,
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """
    Method assigns resources with new eb and pb id.

    Args:
        subarray_id (str): _description_
        central_node_low (CentralNodeWrapperLow): _description_
        event_recorder (EventRecorder): _description_
    """
    assign_input = update_eb_pb_ids(central_node_low.assign_input)
    central_node_low.store_resources(assign_input)

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
