"""Test Timeout for Configure command for SDP, CSP and MCCS Leaf Nodes."""
import json

import pytest
from assertpy import assert_that
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_harness.constant import (
    INTERMEDIATE_CONFIGURING_STATE_DEFECT,
    TIMEOUT,
    low_csp_subarray_leaf_node,
    low_sdp_subarray_leaf_node,
    mccs_subarray_leaf_node,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)


class TestConfigureTimeout:
    """Tests for testing timeout for Configure command on LOW TMC."""

    @pytest.mark.SKA_low
    def test_configure_timeout_csp_ln(
        self,
        subarray_node_low: SubarrayNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """Test timeout on CSP Leaf Nodes for Configure command by inducing
        fault into the system."""
        csp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_DEVICE
        )
        # Event Subscriptions
        event_tracer.subscribe_event(subarray_node_low.subarray_node, "State")
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )

        # Preparing input files
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        log_events(
            {
                subarray_node_low.subarray_node: [
                    "longRunningCommandResult",
                    "obsState",
                ]
            }
        )
        _, unique_id = subarray_node_low.move_to_on()
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ON Command: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )
        subarray_node_low.force_change_of_obs_state("IDLE")
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )
        # Inducing Fault
        csp_subarray_sim.SetDefective(INTERMEDIATE_CONFIGURING_STATE_DEFECT)

        _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in CONFIGURING obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.CONFIGURING,
        )
        exception_message = "Timeout has occurred, command failed"
        result = event_tracer.query_events(
            lambda e: e.has_device(subarray_node_low.subarray_node)
            and e.has_attribute("longRunningCommandResult")
            and e.current_value[0] == unique_id[0]
            and json.loads(e.current_value[1])[0] == ResultCode.FAILED
            and exception_message in json.loads(e.current_value[1])[1]
            and low_csp_subarray_leaf_node
            in json.loads(e.current_value[1])[1],
            timeout=TIMEOUT,
        )

        assert_that(result).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).is_length(1)

    @pytest.mark.SKA_low
    def test_configure_timeout_sdp_ln(
        self,
        subarray_node_low: SubarrayNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """Test timeout on SDP Leaf Nodes for Configure command by inducing
        fault into the system."""
        sdp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )
        # Event Subscriptions
        event_tracer.subscribe_event(subarray_node_low.subarray_node, "State")
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )

        # Preparing input files
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        log_events(
            {
                subarray_node_low.subarray_node: [
                    "longRunningCommandResult",
                    "obsState",
                ]
            }
        )
        _, unique_id = subarray_node_low.move_to_on()
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ON Command: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )
        subarray_node_low.force_change_of_obs_state("IDLE")
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )

        # Inducing Fault
        sdp_subarray_sim.SetDefective(INTERMEDIATE_CONFIGURING_STATE_DEFECT)

        _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in CONFIGURING obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.CONFIGURING,
        )
        exception_message = "Timeout has occurred, command failed"
        result = event_tracer.query_events(
            lambda e: e.has_device(subarray_node_low.subarray_node)
            and e.has_attribute("longRunningCommandResult")
            and e.current_value[0] == unique_id[0]
            and json.loads(e.current_value[1])[0] == ResultCode.FAILED
            and exception_message in json.loads(e.current_value[1])[1]
            and low_sdp_subarray_leaf_node
            in json.loads(e.current_value[1])[1],
            timeout=TIMEOUT,
        )

        assert_that(result).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).is_length(1)

    @pytest.mark.SKA_low
    def test_configure_timeout_mccs_ln(
        self,
        subarray_node_low: SubarrayNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """Test timeout on Mccs Leaf Nodes for Configure command by inducing
        fault into the system."""
        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )
        # Event Subscriptions
        event_tracer.subscribe_event(subarray_node_low.subarray_node, "State")
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )

        # Preparing input files
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        _, unique_id = subarray_node_low.move_to_on()
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ON Command: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )

        subarray_node_low.force_change_of_obs_state("IDLE")

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )

        # Inducing Fault
        mccs_subarray_sim.SetDefective(INTERMEDIATE_CONFIGURING_STATE_DEFECT)

        _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in CONFIGURING obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.CONFIGURING,
        )
        exception_message = "Timeout has occurred, command failed"
        result = event_tracer.query_events(
            lambda e: e.has_device(subarray_node_low.subarray_node)
            and e.has_attribute("longRunningCommandResult")
            and e.current_value[0] == unique_id[0]
            and json.loads(e.current_value[1])[0] == ResultCode.FAILED
            and exception_message in json.loads(e.current_value[1])[1]
            and mccs_subarray_leaf_node in json.loads(e.current_value[1])[1],
            timeout=TIMEOUT,
        )

        assert_that(result).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).is_length(1)
