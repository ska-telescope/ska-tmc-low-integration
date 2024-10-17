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
import time

import pytest
from assertpy import assert_that
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import tmc_low_subarraynode1
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import (
    INTERMEDIATE_STATE_DEFECT,
    RESET_DEFECT,
    TIMEOUT,
)
from tests.tmc.conftest import (
    create_simulators,
    prepare_command_json,
    prepare_resource_json,
    subscribe_to_events,
    verify_assigned_resources,
    verify_empty_assigned_resources,
    verify_initial_state,
    verify_release_resources,
)


class TestLowCentralNodeAssignResources:
    """TMC CentralNode Assign Resources by checking the state transitions of
    simulated master devices (CSP, SDP, MCCS) and the overall
      telescope state."""

    @pytest.mark.SKA_low1
    def test_low_centralnode_assign_resources(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
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
        assign_input_json = prepare_command_json(
            "assign_resources_low", command_input_factory
        )
        release_resource_json = prepare_command_json(
            "release_resources_low", command_input_factory
        )

        (
            assigned_resources_json,
            assigned_resources_json_empty,
        ) = prepare_resource_json()

        # Update transaction and subarray ID
        assign_input_json["transaction_id"] = "txn-....-00002"
        assign_input_json["subarray_id"] = 2

        # Convert to JSON strings
        assigned_resources_json_str = json.dumps(assigned_resources_json)
        assigned_resources_json_empty_str = json.dumps(
            assigned_resources_json_empty
        )

        # Create simulator devices
        simulators = create_simulators(simulator_factory)

        # Subscribe to events
        subscribe_to_events(event_tracer, simulators, central_node_low)

        # Execute ON Command
        central_node_low.move_to_on()
        verify_initial_state(
            event_tracer, simulators, central_node_low, TIMEOUT
        )

        # Execute Assign command
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )
        simulators["mccs_subarray_sim"].SetDirectassignedResources(
            assigned_resources_json_str
        )

        verify_assigned_resources(
            event_tracer,
            simulators,
            central_node_low,
            unique_id,
            assigned_resources_json_str,
            TIMEOUT,
        )

        # Execute release command
        _, unique_id = central_node_low.perform_action(
            "ReleaseResources", release_resource_json
        )
        verify_release_resources(
            event_tracer, simulators, central_node_low, unique_id, TIMEOUT
        )

        # Setting Assigned Resources empty
        simulators["mccs_subarray_sim"].SetDirectassignedResources(
            assigned_resources_json_empty_str
        )
        verify_empty_assigned_resources(
            event_tracer,
            central_node_low,
            assigned_resources_json_empty_str,
            TIMEOUT,
        )

    @pytest.mark.SKA_low
    def test_low_centralnode_assign_resources_exception_propagation(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
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
        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )

        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        log_events(
            {
                central_node_low.central_node: [
                    "longRunningCommandResult",
                    "telescopeState",
                ],
                central_node_low.subarray_node: ["obsState"],
            }
        )
        # Execute ON Command
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
        # Setting device to defective

        mccs_subarray_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
        # Execute Assign command and check command completed successfully
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )

        exception_message = (
            f"{tmc_low_subarraynode1}:"
            " Timeout has "
            "occurred, command failed"
        )

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            central_node_low.central_node,
            [exception_message],
            unique_id[0],
            ResultCode.FAILED,
        )

        mccs_subarray_sim.setDefective(json.dumps(RESET_DEFECT))
        central_node_low.subarray_node.Abort()
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ABORT COMMAND:"
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in ABORTED obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.ABORTED,
        )

    @pytest.mark.SKA_low
    def test_low_centralnode_release_resources_exception_propagation(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
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

        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node,
            "longRunningCommandResult",
        )
        log_events(
            {
                central_node_low.central_node: [
                    "longRunningCommandResult",
                    "telescopeState",
                ],
                central_node_low.subarray_node: ["obsState"],
            }
        )
        # Execute ON Command and verify successful execution
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

        # Execute Assign command and verify successful execution
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )

        # Allowing Subarray Node to finish processing the Assign command
        # completion. Removing the sleep leads to timer thread for Release
        # being stopped by Assign cleanup
        time.sleep(1)

        # Setting device to defective
        sdp_subarray_sim.SetDelayInfo(json.dumps({"ReleaseAllResources": 55}))

        _, unique_id = central_node_low.perform_action(
            "ReleaseResources", release_resource_json
        )

        exception_message = (
            f"{central_node_low.sdp_subarray_leaf_node.dev_name()}:"
            " Timeout has occurred, command failed"
        )

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            central_node_low.central_node,
            [exception_message],
            unique_id[0],
            ResultCode.FAILED,
        )
        sdp_subarray_sim.ResetDelayInfo()
        central_node_low.subarray_node.Abort()

        # Verify ObsState is Aborted
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ABORT COMMAND:"
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in ABORTED obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.ABORTED,
        )
