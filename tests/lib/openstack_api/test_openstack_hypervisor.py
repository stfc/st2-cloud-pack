from unittest.mock import MagicMock
from enums.hypervisor_states import HypervisorState
from openstack_api.openstack_hypervisor import (
    get_avaliable_flavors,
    get_hypervisor_state,
)
import pytest


def test_get_state_running():
    """
    Test hypervisor state is running for given variables
    """
    hypervisor = {
        "hypervisor_uptime_days": 7,
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 5,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.RUNNING


@pytest.mark.parametrize(
    "hypervisor",
    [
        {
            "hypervisor_uptime_days": 70,
            "hypervisor_status": "enabled",
            "hypervisor_state": "up",
            "hypervisor_server_count": 0,
        },
        {
            "hypervisor_uptime_days": 100,
            "hypervisor_status": "enabled",
            "hypervisor_state": "up",
            "hypervisor_server_count": 12,
        },
    ],
)
def test_get_state_pending_maintenance(hypervisor):
    """
    Test hypervisor state is pending maintenace for given variables, even if the hv is empty
    """
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.PENDING_MAINTENANCE


def test_get_state_draining():
    """
    Test hypervisor state is draining for given variables
    """
    hypervisor = {
        "hypervisor_uptime_days": 100,
        "hypervisor_status": "disabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 5,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.DRAINING


def test_get_state_drained():
    """
    Test hypervisor state is drained for given variables
    """
    hypervisor = {
        "hypervisor_uptime_days": 100,
        "hypervisor_status": "disabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 0,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.DRAINED


def test_get_state_rebooted():
    """
    Test hypervisor state is rebooted for given variables
    """
    hypervisor = {
        "hypervisor_uptime_days": 0,
        "hypervisor_status": "disabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 0,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.REBOOTED


def test_get_state_empty():
    """
    Test hypervisor state is empty for given variables
    """
    hypervisor = {
        "hypervisor_uptime_days": 40,
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 0,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.EMPTY


@pytest.mark.parametrize(
    "hypervisor",
    [
        {
            "hypervisor_uptime_days": 40,
            "hypervisor_status": "enabled",
            "hypervisor_state": "down",
            "hypervisor_server_count": 0,
        },
        {
            "hypervisor_uptime_days": 100,
            "hypervisor_status": "disabled",
            "hypervisor_state": "down",
            "hypervisor_server_count": 0,
        },
        {
            "hypervisor_uptime_days": 40,
            "hypervisor_status": "enabled",
            "hypervisor_state": "down",
            "hypervisor_server_count": None,
        },
    ],
)
def test_get_state_down(hypervisor):
    """
    Test hypervisor state is down for given variables, even missing ones.
    """
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.DOWN


@pytest.mark.parametrize(
    "hypervisor",
    [
        {
            "hypervisor_uptime_days": None,
            "hypervisor_status": "enabled",
            "hypervisor_state": "up",
            "hypervisor_server_count": 0,
        },
        {
            "hypervisor_uptime_days": 100,
            "hypervisor_status": None,
            "hypervisor_state": "up",
            "hypervisor_server_count": 0,
        },
        {
            "hypervisor_uptime_days": 40,
            "hypervisor_status": "enabled",
            "hypervisor_state": None,
            "hypervisor_server_count": 2,
        },
        {
            "hypervisor_uptime_days": 40,
            "hypervisor_status": "enabled",
            "hypervisor_state": "up",
            "hypervisor_server_count": None,
        },
        {
            "hypervisor_uptime_days": 5,
            "hypervisor_status": "enabled",
            "hypervisor_state": "up",
            "hypervisor_server_count": -2,
        },
    ],
)
def test_get_unkown_status(hypervisor):
    """
    Test hypervisor state is unknown when missing parameters, when state is up
    """
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.UNKNOWN


def test_missing():
    """
    Test hypervisor state is missing for a missing value in hv_state.
    """
    mock_hv_state = {
        "uptime": True,
        "enabled": False,
        "state": True,
    }
    assert HypervisorState(mock_hv_state) == HypervisorState.UNKNOWN


def test_avaliable_flavors():
    """
    Test avaliable flavors
    """
    mock_conn = MagicMock()
    mock_flavor_1 = MagicMock()
    mock_flavor_2 = MagicMock()
    mock_aggregate_1 = MagicMock()
    mock_aggregate_2 = MagicMock()

    mock_aggregate_1.metadata.return_value = {
        "hosttype": "amdlocal",
        "local-storage-type": "nvme",
    }
    mock_aggregate_1.hosts = ["hvabc.nubes.rl.ac.uk"]
    mock_aggregate_2.metadata.return_value = {
        "hosttype": "amdlocal",
        "local-storage-type": "sas-ssd",
    }
    mock_aggregate_2.hosts = ["hvxyz.nubes.rl.ac.uk"]

    mock_conn.compute.aggregates.return_value = [mock_aggregate_1, mock_aggregate_2]
    mock_conn.compute.flavors.return_value = [mock_flavor_1, mock_flavor_2]

    res = get_avaliable_flavors(mock_conn, "hvxyz.nubes.rl.ac.uk")

    mock_conn.compute.aggregates.assert_called_once()

    mock_aggregate_1.metadata.get.assert_any_call("hosttype")
    mock_aggregate_1.metadata.get.assert_any_call("local-storage-type")
    mock_aggregate_2.metadata.get.assert_any_call("hosttype")
    mock_aggregate_2.metadata.get.assert_any_call("local-storage-type")

    assert mock_aggregate_1.metadata.get.call_count == 2
    assert mock_aggregate_2.metadata.get.call_count == 2

    mock_conn.compute.flavors.assert_called_once()

    assert res == [mock_flavor_1.name, mock_flavor_2.name]
