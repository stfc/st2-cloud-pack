import pytest
from enums.hypervisor_states import HypervisorState
from openstack_api.openstack_hypervisor import get_days_uptime, get_hypervisor_state


def test_get_state_running():
    """
    Test hypervisor state is running for given variables
    """
    hypervisor = {
        "hypervisor_uptime": "13:37:30 up 7 days,  4:29, 19 users,  load average: 0.04, 0.04, 0.0",
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
        "hypervisor_uptime": "13:37:30 up 100 days,  4:29, 19 users,  load average: 0.04, 0.04, 0.0",
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
        "hypervisor_uptime": "13:37:30 up 100 days,  4:29, 19 users,  load average: 0.04, 0.04, 0.0",
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
        "hypervisor_uptime": "13:37:30 up 100 days,  4:29, 19 users,  load average: 0.04, 0.04, 0.0",
        "hypervisor_status": "disabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 0,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.DRAINED


def test_get_state_unkown_status():
    """
    Test hypervisor state is unknown when missing status
    """
    hypervisor = {
        "hypervisor_uptime": "13:37:30 up 100 days,  4:29, 19 users,  load average: 0.04, 0.04, 0.0",
        "hypervisor_status": None,
        "hypervisor_state": "up",
        "hypervisor_server_count": 0,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.UNKNOWN


def test_get_state_unkown_state():
    """
    Test hypervisor state is unknown when missing state
    """
    hypervisor = {
        "hypervisor_uptime": "13:37:30 up 100 days,  4:29, 19 users,  load average: 0.04, 0.04, 0.0",
        "hypervisor_status": "enabled",
        "hypervisor_state": None,
        "hypervisor_server_count": 0,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.UNKNOWN


def test_get_state_unkown_uptime():
    """
    Test hypervisor state is unknown when missing uptime
    """
    hypervisor = {
        "hypervisor_uptime": None,
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 0,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.UNKNOWN


def test_get_state_unkown_server_count():
    """
    Test hypervisor state is unknown when missing server count
    """
    hypervisor = {
        "hypervisor_uptime": "13:37:30 up 100 days,  4:29, 19 users,  load average: 0.04, 0.04, 0.0",
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": None,
    }
    state = get_hypervisor_state(hypervisor, 60)
    assert state == HypervisorState.UNKNOWN


def test_get_state_no_matching_state():
    hypervisor = {
        "hypervisor_uptime": "up 60 days, 12:34",
        "hypervisor_status": "disabled",
        "hypervisor_state": "down",
        "hypervisor_server_count": 10,
    }
    result = get_hypervisor_state(hypervisor, 60)
    assert result == HypervisorState.UNKNOWN


def test_get_days_uptime_success():
    mock_uptime = (
        "13:37:30 up 100 days,  4:29, 19 users,  load average: 0.04, 0.04, 0.0"
    )
    assert get_days_uptime(mock_uptime) == 100


def test_get_days_uptime_failure():
    mock_uptime = "4:29, 19 users,  load average: 0.04, 0.04, 0.0"
    with pytest.raises(ValueError):
        get_days_uptime(mock_uptime)
