"""Confest"""
import json

from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from tango import DevState

from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


def prepare_command_json(command, command_input_factory):
    """
    Prepare the JSON arguments for a central node command.

    Args:
        command (str): The command to prepare.
        command_input_factory (function): A factory function to create
        command inputs.

    Returns:
        dict: The JSON arguments prepared for the command.
    """
    return prepare_json_args_for_centralnode_commands(
        command, command_input_factory
    )


def prepare_resource_json():
    """
    Prepare the JSON structures for assigned resources.

    Returns:
        tuple: A tuple containing two dictionaries:
            - Assigned resources with some IDs.
            - Assigned resources with empty lists.
    """
    assigned_resources_json = {
        "subarray_beam_ids": ["some_id"],
        "station_ids": ["station1", "station2"],
        "apertures": ["AP001.01", "AP001.02"],
        "channels": [32],
    }
    assigned_resources_json_empty = {
        "subarray_beam_ids": [],
        "station_ids": [],
        "apertures": [],
        "channels": [0],
    }
    return assigned_resources_json, assigned_resources_json_empty


# pylint: disable=line-too-long
def create_simulators(simulator_factory):
    """
    Create simulator devices using the provided factory.

    Args:
        simulator_factory: An object responsible for creating simulator d
        evices.

    Returns:
        dict: A dictionary of simulator devices keyed by their names.
    """
    return {
        "csp_subarray_sim": simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_DEVICE
        ),
        "sdp_subarray_sim": simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        ),
        "mccs_controller_sim": simulator_factory.get_or_create_simulator_device(  # noqa: E501
            SimulatorDeviceType.MCCS_MASTER_DEVICE
        ),
        "mccs_subarray_sim": simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        ),
    }


# pylint: enable=line-too-long


def subscribe_to_events(event_tracer, simulators, central_node_low):
    """
    Subscribe to state and observation events for the given simulators and
    nodes.

    Args:
        event_tracer: An object used to trace events.
        simulators (dict): A dictionary of simulator devices.
        central_node_low: An object representing the central node.
    """
    for sim in simulators.values():
        event_tracer.subscribe_event(sim, "State")
        event_tracer.subscribe_event(sim, "obsState")
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_low.subarray_node, "assignedResources"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )


def verify_initial_state(event_tracer, simulators, central_node_low, timeout):
    """
    Verify that the initial state of simulators and the central node is ON.

    Args:
        event_tracer: An object used to trace events.
        simulators (dict): A dictionary of simulator devices.
        central_node_low: An object representing the central node.
        timeout (int): The timeout period for verification.
    """
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            simulators["csp_subarray_sim"], "State", DevState.ON
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            simulators["mccs_controller_sim"], "State", DevState.ON
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            central_node_low.central_node, "telescopeState", DevState.ON
        )
    )


def verify_assigned_resources(
    event_tracer,
    simulators,
    central_node_low,
    unique_id,
    assigned_resources_json_str,
    timeout,
):
    """
    Verify that the assigned resources have been updated correctly.

    Args:
        event_tracer: An object used to trace events.
        simulators (dict): A dictionary of simulator devices.
        central_node_low: An object representing the central node.
        unique_id (tuple): A tuple containing a unique identifier.
        assigned_resources_json_str (str): The JSON string
        representing assigned resources.
        timeout (int): The timeout period for verification.
    """
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            simulators["sdp_subarray_sim"], "obsState", ObsState.IDLE
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            simulators["csp_subarray_sim"], "obsState", ObsState.IDLE
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            simulators["mccs_subarray_sim"], "obsState", ObsState.IDLE
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            central_node_low.subarray_node, "obsState", ObsState.IDLE
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            central_node_low.subarray_node,
            "assignedResources",
            (assigned_resources_json_str,),
        )
    )


def verify_release_resources(
    event_tracer, simulators, central_node_low, unique_id, timeout
):
    """
    Verify that the resources have been released correctly.

    Args:
        event_tracer: An object used to trace events.
        simulators (dict): A dictionary of simulator devices.
        central_node_low: An object representing the central node.
        unique_id (tuple): A tuple containing a unique identifier.
        timeout (int): The timeout period for verification.
    """
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            simulators["sdp_subarray_sim"], "obsState", ObsState.EMPTY
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            simulators["csp_subarray_sim"], "obsState", ObsState.EMPTY
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            simulators["mccs_subarray_sim"], "obsState", ObsState.EMPTY
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            central_node_low.subarray_node, "obsState", ObsState.EMPTY
        )
    )
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )
    )


def verify_empty_assigned_resources(
    event_tracer, central_node_low, assigned_resources_json_empty_str, timeout
):
    """
    Verify that the assigned resources are empty.

    Args:
        event_tracer: An object used to trace events.
        central_node_low: An object representing the central node.
        assigned_resources_json_empty_str (str): The JSON string representing
        empty assigned resources.
        timeout (int): The timeout period for verification.
    """
    assert (
        (event_tracer)
        .within_timeout(timeout)
        .has_change_event_occurred(
            central_node_low.subarray_node,
            "assignedResources",
            (assigned_resources_json_empty_str,),
        )
    )
