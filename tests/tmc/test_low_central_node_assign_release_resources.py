"""
This module contains test cases for the low-level CentralNode functionality
related to the AssignResources command.It utilizes the pytest framework and
mocks certain components for testing purposes.
The test cases cover various scenarios, including the successful execution of
the AssignResources command,
verification of attribute updates, exception handling, and proper propagation
of exceptions.
"""
import json

import pytest
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from tango import DevState

from tests.resources.test_harness.constant import (
    low_sdp_subarray_leaf_node,
    mccs_controller,
    mccs_master_leaf_node,
    tmc_low_subarraynode1,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.common_helpers import Waiter
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    wait_for_attribute_update,
)
from tests.resources.test_support.constant_low import (
    FAILED_RESULT_DEFECT,
    RESET_DEFECT,
)


def check_assigned_resources_attribute_after_release(
    assigned_resources_attribute_value,
):
    """
    This function will verify if assignedResources attribute is set to
    empty values after release resources is completed.
    """
    assigned_resources = json.loads(assigned_resources_attribute_value[0])
    assert assigned_resources["subarray_beam_ids"] == []
    assert assigned_resources["station_beam_ids"] == []
    assert assigned_resources["station_ids"] == []
    assert assigned_resources["apertures"] == []
    assert assigned_resources["channels"] == [0]


def check_assigned_resources_attribute_after_assign(
    assigned_resources_attribute_value,
):
    """
    This function will verify if assignedResources attribute is set to
    expected values after assign resources command is completed.
    """

    assigned_resources = json.loads(assigned_resources_attribute_value[0])
    assert assigned_resources["subarray_beam_ids"] == ["1"]
    assert assigned_resources["channels"] == [32]
    assert assigned_resources["station_ids"] == ["1", "2", "3"]
    assert assigned_resources["apertures"] == [
        "AP001.01",
        "AP001.02",
        "AP002.01",
        "AP002.02",
        "AP003.01",
    ]


class TestLowCentralNodeAssignResources:
    """TMC CentralNode Assign Resources by checking the state transitions of
    simulated master devices (CSP, SDP, MCCS) and the overall
      telescope state."""

    @pytest.mark.SKA_low
    def test_low_centralnode_assign_resources(
        self,
        central_node_low,
        event_recorder,
        simulator_factory,
        command_input_factory,
    ):
        """
        Test to verify transitions that are triggered by AssignResources
        command and followed by a completion transition
        assuming that external subsystems work fine.
        Glossary:
        - "central_node_low": fixture for a TMC CentralNode Low under test
        which provides simulated master devices
        - "event_recorder": fixture for a MockTangoEventCallbackGroup
        for validating the subscribing and receiving events.
        - "simulator_factory": fixtur for creating simulator devices for
        low Telescope respectively.
        - "command_input_factory": fixture for JsonFactory class,
        which provides json files for CentralNode
        """
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )

        release_resource_json = prepare_json_args_for_centralnode_commands(
            "release_resources_low", command_input_factory
        )

        assigned_resources_json = prepare_json_args_for_commands(
            "AssignedResources_low", command_input_factory
        )

        assigned_resources_json_empty = prepare_json_args_for_commands(
            "AssignedResources_low_empty", command_input_factory
        )

        csp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_DEVICE
        )
        sdp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )
        mccs_controller_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_MASTER_DEVICE
        )

        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )

        event_recorder.subscribe_event(csp_subarray_sim, "State")
        event_recorder.subscribe_event(sdp_subarray_sim, "State")
        event_recorder.subscribe_event(mccs_controller_sim, "State")
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_recorder.subscribe_event(csp_subarray_sim, "obsState")
        event_recorder.subscribe_event(sdp_subarray_sim, "obsState")
        event_recorder.subscribe_event(mccs_subarray_sim, "obsState")
        event_recorder.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_recorder.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )

        # Execute ON Command
        central_node_low.move_to_on()

        assert event_recorder.has_change_event_occurred(
            csp_subarray_sim,
            "State",
            DevState.ON,
        )
        assert event_recorder.has_change_event_occurred(
            sdp_subarray_sim,
            "State",
            DevState.ON,
        )
        assert event_recorder.has_change_event_occurred(
            mccs_controller_sim,
            "State",
            DevState.ON,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )

        # Execute Assign command and check command completed successfully
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )

        mccs_subarray_sim.SetDirectassignedResources(assigned_resources_json)

        assert event_recorder.has_change_event_occurred(
            sdp_subarray_sim,
            "obsState",
            ObsState.IDLE,
        )
        assert event_recorder.has_change_event_occurred(
            csp_subarray_sim,
            "obsState",
            ObsState.IDLE,
        )
        assert event_recorder.has_change_event_occurred(
            mccs_subarray_sim,
            "obsState",
            ObsState.IDLE,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )

        assert wait_for_attribute_update(
            central_node_low.subarray_node,
            "longRunningCommandResult",
            "AssignResources",
            ResultCode.OK,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], str(ResultCode.OK.value)),
        )

        assigned_resources_attribute_value = (
            central_node_low.subarray_node.assignedResources
        )

        check_assigned_resources_attribute_after_assign(
            assigned_resources_attribute_value
        )

        # Execute release command and verify command completed successfully

        _, unique_id = central_node_low.perform_action(
            "ReleaseResources", release_resource_json
        )

        assert event_recorder.has_change_event_occurred(
            sdp_subarray_sim,
            "obsState",
            ObsState.EMPTY,
        )
        assert event_recorder.has_change_event_occurred(
            csp_subarray_sim,
            "obsState",
            ObsState.EMPTY,
        )
        assert event_recorder.has_change_event_occurred(
            mccs_subarray_sim,
            "obsState",
            ObsState.EMPTY,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], str(ResultCode.OK.value)),
        )

        assert central_node_low.subarray_node.obsState == ObsState.EMPTY

        # Setting Assigned Resources empty

        mccs_subarray_sim.SetDirectassignedResources(
            assigned_resources_json_empty
        )

        assigned_resources_attribute_value = (
            central_node_low.subarray_node.assignedResources
        )
        check_assigned_resources_attribute_after_release(
            assigned_resources_attribute_value
        )

    @pytest.mark.SKA_low
    def test_low_centralnode_assign_resources_exception_propagation(
        self,
        central_node_low,
        event_recorder,
        simulator_factory,
        command_input_factory,
    ):
        """
        Test to verify the exception received on longRunningCommandResult
        attribute when AssignResources command in invoked on CentralNode.

        Glossary:
        - "central_node_low": fixture for a TMC CentralNode Low under test
        which provides simulated master devices
        - "event_recorder": fixture for a MockTangoEventCallbackGroup
        for validating the subscribing and receiving events.
        - "simulator_factory": fixture for creating simulator devices for
        low Telescope respectively.
        - "command_input_factory": fixture for JsonFactory class,
        which provides json files for CentralNode
        """
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )
        mccs_controller_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_MASTER_DEVICE
        )

        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_recorder.subscribe_event(
            central_node_low.central_node,
            "longRunningCommandResult",
            timeout=80.0,
        )

        # Execute ON Command
        central_node_low.move_to_on()

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )
        # Setting device to defective
        mccs_controller_sim.SetRaiseException(True)

        # Execute Assign command and check command completed successfully
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )

        exception_message = (
            "Exception occurred on the following devices: "
            + f"{mccs_master_leaf_node}: Exception "
            "occurred on device: " + f"{mccs_controller}: Exception "
            "occured on device: "
            + f"{mccs_controller}{tmc_low_subarraynode1}:"
            " Timeout has "
            "occurred, command failed"
        )

        expected_long_running_command_result = (
            unique_id[0],
            exception_message,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            expected_long_running_command_result,
        )
        mccs_controller_sim.SetRaiseException(False)
        central_node_low.subarray_node.Abort()

        # Verify ObsState is Aborted
        the_waiter = Waiter()
        the_waiter.set_wait_for_specific_obsstate(
            "ABORTED", [tmc_low_subarraynode1]
        )
        the_waiter.wait(200)

    @pytest.mark.SKA_low
    def test_low_centralnode_release_resources_exception_propagation(
        self,
        central_node_low,
        event_recorder,
        simulator_factory,
        command_input_factory,
    ):
        """
        Test to verify the exception received on longRunningCommandResult
        attribute when AssignResources command in invoked on CentralNode.

        Glossary:
        - "central_node_low": fixture for a TMC CentralNode Low under test
        which provides simulated master devices
        - "event_recorder": fixture for a MockTangoEventCallbackGroup
        for validating the subscribing and receiving events.
        - "simulator_factory": fixture for creating simulator devices for
        low Telescope respectively.
        - "command_input_factory": fixture for JsonFactory class,
        which provides json files for CentralNode
        """
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )
        release_resource_json = prepare_json_args_for_centralnode_commands(
            "release_resources_low", command_input_factory
        )
        sdp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )

        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_recorder.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_recorder.subscribe_event(
            central_node_low.central_node,
            "longRunningCommandResult",
            timeout=80.0,
        )

        # Execute ON Command and verify successful execution
        central_node_low.move_to_on()

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )

        # Execute Assign command and verify successful execution
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )

        assert event_recorder.has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
            lookahead=25,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], str(ResultCode.OK.value)),
        )
        # Execute ReleaseResources and verify error propagation

        # Setting device to defective
        sdp_subarray_sim.SetDefective(json.dumps(FAILED_RESULT_DEFECT))

        _, unique_id = central_node_low.perform_action(
            "ReleaseResources", release_resource_json
        )

        exception_message = (
            "Exception occurred on the following devices: "
            + f"{tmc_low_subarraynode1}: Exception occurred on the following "
            + f"devices:\n{low_sdp_subarray_leaf_node}:"
            " Timeout has occured, command failed\n"
        )

        expected_long_running_command_result = (
            unique_id[0],
            exception_message,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            expected_long_running_command_result,
        )
        sdp_subarray_sim.SetDefective(json.dumps(RESET_DEFECT))
        central_node_low.subarray_node.Abort()

        # Verify ObsState is Aborted
        the_waiter = Waiter()
        the_waiter.set_wait_for_specific_obsstate(
            "ABORTED", [tmc_low_subarraynode1]
        )
        the_waiter.wait(200)
