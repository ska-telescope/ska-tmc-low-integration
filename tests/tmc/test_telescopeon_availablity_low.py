"""
This module contains test cases related to the execution of commands
(AssignResources, ReleaseResources, TelescopeOn) while the corresponding pods
are manually deleted.
"""
import pytest

from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)

# Note:These test case will pass only when any of the node
# is deleted explicitly
# Hence this test will be skipped on pipeline
# Sample command to delete is
# while true;
# do kubectl delete pod/subarraynode-02-0 -n ska-tmc-integration; sleep 3;
# done


@pytest.mark.skip(reason="Unskip after repository setup")
@pytest.mark.SKA_low
def test_assign(command_input_factory, central_node_low):
    """AssignResources  is executed while pods are deleted."""

    assign_json = prepare_json_args_for_centralnode_commands(
        "command_assign_resources_low", command_input_factory
    )
    _, message = central_node_low.store_resources(assign_json)
    assert "Subarray ska_low/tm_subarray_node/1 is not available" in str(
        message
    )


@pytest.mark.skip(reason="Unskip after repository setup")
@pytest.mark.SKA_low
def test_release(command_input_factory, central_node_low):
    """ReleaseResources is executed while pods are deleted."""

    release_json = prepare_json_args_for_centralnode_commands(
        "command_release_resources_low", command_input_factory
    )
    _, message = central_node_low.invoke_release_resources(release_json)

    assert "Subarray ska_low/tm_subarray_node/1 is not available" in str(
        message
    )


@pytest.mark.skip(reason="Unskip after repository setup")
@pytest.mark.SKA_low
def test_telescope_on(central_node_low):
    """On Command  is executed while pods are deleted."""

    with pytest.raises(Exception) as info:
        # tmc.set_to_on()
        central_node_low.move_to_on()

    assert "not available" in str(info.value)


@pytest.mark.skip(reason="Unskip after repository setup")
@pytest.mark.SKA_low
def test_assign_sn_entrypoint_low(command_input_factory, central_node_low):
    """AssignResources is executed while pods are deleted."""
    assign_json = prepare_json_args_for_centralnode_commands(
        "command_release_resources_low", command_input_factory
    )
    with pytest.raises(Exception) as info:
        central_node_low.subarray_node.AssignResources(assign_json)

    assert "Tmc Subarray is not available" in str(info.value)


@pytest.mark.skip(reason="Unskip after repository setup")
@pytest.mark.SKA_low
def test_release_sn_entrypoint_low(central_node_low):
    """ReleaseResources is executed while pods are deleted."""

    with pytest.raises(Exception) as info:
        central_node_low.subarray_node.ReleaseAllResources()

    assert "Tmc Subarray is not available" in str(info.value)
