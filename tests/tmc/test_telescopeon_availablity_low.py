"""
This module contains test cases related to the execution of commands
(AssignResources, ReleaseResources, TelescopeOn) while the corresponding pods
are manually deleted.
"""
import pytest
from tango import DeviceProxy

from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import (
    centralnode,
    tmc_subarraynode1,
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
def test_assign(command_input_factory):
    """AssignResources  is executed while pods are deleted."""

    assign_json = prepare_json_args_for_centralnode_commands(
        "command_assign_resources_low", command_input_factory
    )
    central_node = DeviceProxy(centralnode)
    _, message = central_node.AssignResources(assign_json)
    assert "Subarray ska_low/tm_subarray_node/1 is not available" in str(
        message
    )


@pytest.mark.skip(reason="Unskip after repository setup")
@pytest.mark.SKA_low
def test_release(command_input_factory):
    """ReleaseResources is executed while pods are deleted."""

    release_json = prepare_json_args_for_centralnode_commands(
        "command_release_resources_low", command_input_factory
    )
    central_node = DeviceProxy(centralnode)
    _, message = central_node.ReleaseResources(release_json)

    assert "Subarray ska_low/tm_subarray_node/1 is not available" in str(
        message
    )


@pytest.mark.skip(reason="Unskip after repository setup")
@pytest.mark.SKA_low
def test_telescope_on():
    """On Command  is executed while pods are deleted."""
    central_node = DeviceProxy(centralnode)

    # works fine when pods are deleted
    with pytest.raises(Exception) as info:
        # tmc.set_to_on()
        central_node.TelescopeOn()

    assert "not available" in str(info.value)


@pytest.mark.skip(reason="Unskip after repository setup")
@pytest.mark.SKA_low
def test_assign_sn_entrypoint_low(command_input_factory):
    """AssignResources is executed while pods are deleted."""
    assign_json = prepare_json_args_for_centralnode_commands(
        "command_release_resources_low", command_input_factory
    )

    tmcsubarraynode1 = DeviceProxy(tmc_subarraynode1)
    with pytest.raises(Exception) as info:
        tmcsubarraynode1.AssignResources(assign_json)

    assert "Tmc Subarray is not available" in str(info.value)


@pytest.mark.skip(reason="Unskip after repository setup")
@pytest.mark.SKA_low
def test_release_sn_entrypoint_low(json_factory):
    """ReleaseResources is executed while pods are deleted."""

    tmcsubarraynode1 = DeviceProxy(tmc_subarraynode1)
    with pytest.raises(Exception) as info:
        tmcsubarraynode1.ReleaseAllResources()

    assert "Tmc Subarray is not available" in str(info.value)
