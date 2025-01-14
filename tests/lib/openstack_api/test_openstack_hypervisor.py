from enums.hypervisor_states import HypervisorState
from openstack_api.openstack_hypervisor import get_hypervisor_state
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


def test_get_state_pending_maintenance():
    """
    Test hypervisor state is pending maintenace for given variables
    """
    hypervisor = {
        "hypervisor_uptime_days": 100,
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 5,
    }
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
            "hypervisor_server_count": 2,
        },
    ],
)
def test_get_state_down(hypervisor):
    """
    Test hypervisor state is drained for given variables
    """
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.DOWN


@pytest.mark.parametrize(
    "hypervisor",
    [
        {
            "hypervisor_uptime_days": None,
            "hypervisor_status": "enabled",
            "hypervisor_state": "down",
            "hypervisor_server_count": 0,
        },
        {
            "hypervisor_uptime_days": 100,
            "hypervisor_status": None,
            "hypervisor_state": "down",
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
            "hypervisor_state": None,
            "hypervisor_server_count": None,
        },
    ],
)
def test_get_unkown_status(hypervisor):
    """
    Test hypervisor state is unknown when missing parameters
    """
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.UNKNOWN
