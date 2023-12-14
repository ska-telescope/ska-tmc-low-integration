import pytest
from ska_control_model import ObsState

from tests.resources.test_harness.helpers import (
    check_assigned_resources,
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
)


class TestMidCentralNodeAssignResources(object):
    @pytest.mark.SKA_mid
    def test_mid_centralnode_assign_resources(
        self,
        central_node_mid,
        event_recorder,
        simulator_factory,
        command_input_factory,
    ):
        """
        Test to verify transitions that are triggered by AssignResources and
        ReleaseResource command and followed by a completion transition
        assuming that external subsystems work fine.
        Glossary:
        - "central_node_mid": fixture for a TMC CentralNode Mid under test
        which provides simulated master devices
        - "event_recorder": fixture for a MockTangoEventCallbackGroup
        for validating the subscribing and receiving events.
        - "simulator_factory": fixture for creating simulator devices for
        mid Telescope respectively.
        - "command_input_factory": fixture for JsonFactory class,
        which provides json files for CentralNode
        """

        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_mid", command_input_factory
        )
        csp_sim, sdp_sim, _, _ = get_device_simulators(simulator_factory)
        event_recorder.subscribe_event(csp_sim, "obsState")
        event_recorder.subscribe_event(sdp_sim, "obsState")
        event_recorder.subscribe_event(
            central_node_mid.subarray_node, "obsState"
        )
        event_recorder.subscribe_event(
            central_node_mid.subarray_node, "assignedResources"
        )
        central_node_mid.move_to_on()
        central_node_mid.perform_action("AssignResources", assign_input_json)
        assert event_recorder.has_change_event_occurred(
            sdp_sim,
            "obsState",
            ObsState.IDLE,
        )
        assert event_recorder.has_change_event_occurred(
            csp_sim,
            "obsState",
            ObsState.IDLE,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.subarray_node,
            "obsState",
            ObsState.IDLE,
        )
        assert check_assigned_resources(
            central_node_mid.subarray_node, ("SKA001", "SKA002")
        )
