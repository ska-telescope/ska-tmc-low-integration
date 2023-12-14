import pytest
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.helpers import check_subarray_obs_state


class TestSubarrayNodeAbortCommandObsStateTransitions(object):
    @pytest.mark.parametrize(
        "source_obs_state",
        ["RESOURCING", "IDLE", "CONFIGURING", "READY", "SCANNING"],
    )
    @pytest.mark.skip(reason="Configure issue")
    @pytest.mark.SKA_mid
    def test_subarray_obs_transitions_valid_data(
        self,
        subarray_node,
        event_recorder,
        source_obs_state,
    ):
        """
        Test to verify transitions that are triggered by Abort
        command and followed by a completion transition
        that start with a transient state.
        assuming that external subsystems work fine.
        Glossary:
        - "subarray_node": fixture for a TMC SubarrayNode under test
        which provides simulated subarray and master devices
        - "source_obs_state": a TMC SubarrayNode initial allowed obsState,
           required to invoke Abort command
        """

        event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
        event_recorder.subscribe_event(
            subarray_node.csp_subarray_leaf_node, "cspSubarrayObsState"
        )
        event_recorder.subscribe_event(
            subarray_node.sdp_subarray_leaf_node, "sdpSubarrayObsState"
        )

        subarray_node.move_to_on()
        subarray_node.force_change_of_obs_state(source_obs_state)

        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "obsState",
            ObsState[source_obs_state],
            lookahead=15,
        )

        assert event_recorder.has_change_event_occurred(
            subarray_node.csp_subarray_leaf_node,
            "cspSubarrayObsState",
            ObsState[source_obs_state],
            lookahead=15,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.sdp_subarray_leaf_node,
            "sdpSubarrayObsState",
            ObsState[source_obs_state],
            lookahead=15,
        )

        subarray_node.execute_transition("Abort", argin=None)

        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "obsState",
            ObsState.ABORTING,
            lookahead=15,
        )

        assert event_recorder.has_change_event_occurred(
            subarray_node.sdp_subarray_leaf_node,
            "sdpSubarrayObsState",
            ObsState.ABORTED,
            lookahead=15,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.csp_subarray_leaf_node,
            "cspSubarrayObsState",
            ObsState.ABORTED,
            lookahead=15,
        )
        assert check_subarray_obs_state(obs_state="ABORTED")
