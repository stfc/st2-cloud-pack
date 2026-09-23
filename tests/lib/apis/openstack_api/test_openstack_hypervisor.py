from unittest.mock import MagicMock, NonCallableMock, patch
from apis.openstack_api.enums.hypervisor_enums import HypervisorAction
from apis.openstack_api.openstack_hypervisor import (
    Hypervisor,
    get_available_flavors,
)
import pytest


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity")
@pytest.mark.parametrize(
    ("hypervisor_data", "aggregate_capacity"),
    [
        (
            {
                "hypervisor_name": "host0",
                "hypervisor_uptime_days": 10.0,
                "hypervisor_status": "enabled",
                "hypervisor_state": "up",
                "hypervisor_server_count": 0,
                "hypervisor_disabled_reason": None,
            },
            0.1,
        ),
        (
            {
                "hypervisor_name": "host1",
                "hypervisor_uptime_days": 20.0,
                "hypervisor_status": "enabled",
                "hypervisor_state": "up",
                "hypervisor_server_count": 12,
                "hypervisor_disabled_reason": None,
            },
            0.5,
        ),
    ],
)
def test_no_maintenance_needed(
    mock_get_capacity,
    mock_connect,
    hypervisor_data,
    aggregate_capacity,
):
    """
    Test hypervisor state is running for given variables
    """
    mock_connect.return_value = MagicMock()
    mock_get_capacity.return_value = aggregate_capacity
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == HypervisorAction.NOOP


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity")
@pytest.mark.parametrize(
    ("hypervisor_data", "aggregate_capacity"),
    [
        (
            {
                "hypervisor_name": "host0",
                "hypervisor_uptime_days": 10.0,
                "hypervisor_status": "disabled",
                "hypervisor_state": "up",
                "hypervisor_server_count": 0,
                "hypervisor_disabled_reason": "2026/09/22 - HW Fault - AB",
            },
            0.1,
        ),
        (
            {
                "hypervisor_name": "host1",
                "hypervisor_uptime_days": 20.0,
                "hypervisor_status": "disabled",
                "hypervisor_state": "up",
                "hypervisor_server_count": 12,
                "hypervisor_disabled_reason": None,
            },
            0.5,
        ),
    ],
)
def test_ignore_manually_disabled(
    mock_get_capacity,
    mock_connect,
    hypervisor_data,
    aggregate_capacity,
):
    """
    Test hypervisor state is running for given variables
    """
    mock_connect.return_value = MagicMock()
    mock_get_capacity.return_value = aggregate_capacity
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == HypervisorAction.NOOP


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity")
@pytest.mark.parametrize(
    ("hypervisor_data", "aggregate_capacity"),
    [
        (
            {
                "hypervisor_name": "host0",
                "hypervisor_uptime_days": 10.0,
                "hypervisor_status": "disabled",
                "hypervisor_state": "down",
                "hypervisor_server_count": 0,
                "hypervisor_disabled_reason": "2026/09/22 - HW Fault - AB",
            },
            0.1,
        ),
        (
            {
                "hypervisor_name": "host1",
                "hypervisor_uptime_days": 20.0,
                "hypervisor_status": "disabled",
                "hypervisor_state": "up",
                "hypervisor_server_count": 12,
                "hypervisor_disabled_reason": None,
            },
            0.5,
        ),
        (
            {
                "hypervisor_name": "host2",
                "hypervisor_uptime_days": 100.0,
                "hypervisor_status": "enabled",
                "hypervisor_state": "down",
                "hypervisor_server_count": 10,
                "hypervisor_disabled_reason": None,
            },
            0.1,
        ),
        (
            {
                "hypervisor_name": "host3",
                "hypervisor_uptime_days": 20.0,
                "hypervisor_status": "enabled",
                "hypervisor_state": "down",
                "hypervisor_server_count": 0,
                "hypervisor_disabled_reason": None,
            },
            0.5,
        ),
    ],
)
def test_ignore_down_hosts(
    mock_get_capacity,
    mock_connect,
    hypervisor_data,
    aggregate_capacity,
):
    """
    Test hypervisor state is running for given variables
    """
    mock_connect.return_value = MagicMock()
    mock_get_capacity.return_value = aggregate_capacity
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == HypervisorAction.NOOP


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity")
@pytest.mark.parametrize(
    ("hypervisor_data", "aggregate_capacity", "expected_action"),
    [
        (
            {
                "hypervisor_name": "host0",
                "hypervisor_uptime_days": 70.0,
                "hypervisor_status": "enabled",
                "hypervisor_state": "up",
                "hypervisor_server_count": 0,
                "hypervisor_disabled_reason": None,
            },
            0.1,
            HypervisorAction.DRAIN,
        ),
        (
            {
                "hypervisor_name": "host1",
                "hypervisor_uptime_days": 100.0,
                "hypervisor_status": "enabled",
                "hypervisor_state": "up",
                "hypervisor_server_count": 12,
                "hypervisor_disabled_reason": None,
            },
            0.5,
            HypervisorAction.NOOP,
        ),
        (
            {
                "hypervisor_name": "host2",
                "hypervisor_uptime_days": 100.0,
                "hypervisor_status": "disabled",
                "hypervisor_state": "up",
                "hypervisor_server_count": 0,
                "hypervisor_disabled_reason": "Stackstorm: Drained",
            },
            0.1,
            HypervisorAction.PATCH,
        ),
        (
            {
                "hypervisor_name": "host3",
                "hypervisor_uptime_days": 100.0,
                "hypervisor_status": "disabled",
                "hypervisor_state": "up",
                "hypervisor_server_count": 0,
                "hypervisor_disabled_reason": "Stackstorm: Drained",
            },
            0.6,
            HypervisorAction.PATCH,
        ),
    ],
)
def test_maintenance_action(
    mock_get_capacity,
    mock_connect,
    hypervisor_data,
    aggregate_capacity,
    expected_action,
):
    """
    Test hypervisor state is pending maintenace for given variables, even if the hv is empty
    """
    mock_connect.return_value = MagicMock()
    mock_get_capacity.return_value = aggregate_capacity
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == expected_action


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity", return_value=0.1)
@pytest.mark.parametrize("hostname", [None, 123, {"host": "host0"}])
def test_garbage_hostname(_mock_get_capacity, mock_connect, hostname):
    """
    Test hypervisor state is unknown when missing parameters, when state is up
    """
    hypervisor_data = {
        "hypervisor_name": hostname,
        "hypervisor_uptime_days": 100.0,
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 0,
        "hypervisor_disabled_reason": None,
    }
    mock_connect.return_value = MagicMock()
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == HypervisorAction.NOOP


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity", return_value=0.1)
@pytest.mark.parametrize("uptime", [None, "123", 123, {"uptime": 123}])
def test_garbage_uptime(_mock_get_capacity, mock_connect, uptime):
    """
    Test hypervisor state is unknown when missing parameters, when state is up
    """
    hypervisor_data = {
        "hypervisor_name": "host0",
        "hypervisor_uptime_days": uptime,
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 0,
        "hypervisor_disabled_reason": None,
    }
    mock_connect.return_value = MagicMock()
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == HypervisorAction.NOOP


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity", return_value=0.1)
@pytest.mark.parametrize("status", [None, "re-enabled", 1, {"enabled": True}])
def test_garbage_status(_mock_get_capacity, mock_connect, status):
    """
    Test hypervisor state is unknown when missing parameters, when state is up
    """
    hypervisor_data = {
        "hypervisor_name": "host0",
        "hypervisor_uptime_days": 123.0,
        "hypervisor_status": status,
        "hypervisor_state": "up",
        "hypervisor_server_count": 0,
        "hypervisor_disabled_reason": None,
    }
    mock_connect.return_value = MagicMock()
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == HypervisorAction.NOOP


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity", return_value=0.1)
@pytest.mark.parametrize("state", [None, "started", 1, {"up": True}])
def test_garbage_state(_mock_get_capacity, mock_connect, state):
    """
    Test hypervisor state is unknown when missing parameters, when state is up
    """
    hypervisor_data = {
        "hypervisor_name": "host0",
        "hypervisor_uptime_days": 123.0,
        "hypervisor_status": "enabled",
        "hypervisor_state": state,
        "hypervisor_server_count": 0,
        "hypervisor_disabled_reason": None,
    }
    mock_connect.return_value = MagicMock()
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == HypervisorAction.NOOP


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity", return_value=0.1)
@pytest.mark.parametrize("server_count", [None, "10", -1, 10.0, {"count": 10}])
def test_garbage_server_count(_mock_get_capacity, mock_connect, server_count):
    """
    Test hypervisor state is unknown when missing parameters, when state is up
    """
    hypervisor_data = {
        "hypervisor_name": "host0",
        "hypervisor_uptime_days": 123.0,
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": server_count,
        "hypervisor_disabled_reason": None,
    }
    mock_connect.return_value = MagicMock()
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == HypervisorAction.NOOP


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
@patch.object(Hypervisor, "get_aggregate_capacity", return_value=0.1)
@pytest.mark.parametrize("disabled_reason", [-1, 10.0, {"reason": "HW fault"}])
def test_garbage_disabled_reason(_mock_get_capacity, mock_connect, disabled_reason):
    """
    Test hypervisor state is unknown when missing parameters, when state is up
    """
    hypervisor_data = {
        "hypervisor_name": "host0",
        "hypervisor_uptime_days": 123.0,
        "hypervisor_status": "disabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 10,
        "hypervisor_disabled_reason": disabled_reason,
    }
    mock_connect.return_value = MagicMock()
    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    action = hypervisor.take_action(uptime_limit=60)
    assert action == HypervisorAction.NOOP


# pylint:disable=too-many-locals
@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
def test_get_aggregate_capacity(mock_connect):
    """
    Docstring for test_get_aggregate_capacity
    """
    hypervisor_data = {
        "hypervisor_name": "host_1",
        "hypervisor_uptime_days": 123.0,
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 10,
        "hypervisor_disabled_reason": None,
    }
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    mock_agg1 = NonCallableMock()
    mock_agg1.name = "agg1"
    mock_agg1.hosts = ["host_0", "host_1", "host_2", "host_3"]
    mock_agg2 = NonCallableMock()
    mock_agg2.name = "agg2"
    mock_agg2.hosts = ["host_a", "host_b"]
    mock_agg3 = NonCallableMock()
    mock_agg3.name = "agg3"
    mock_agg3.hosts = ["host_1", "host_alpha", "host_bar"]

    mock_host_0 = NonCallableMock()
    mock_host_0.name = "host_0"
    mock_host_0.status = "enabled"
    mock_host_1 = NonCallableMock()
    mock_host_1.name = "host_1"
    mock_host_1.status = "disabled"
    mock_host_2 = NonCallableMock()
    mock_host_2.name = "host_2"
    mock_host_2.status = "enabled"

    mock_host_3 = NonCallableMock()
    mock_host_3.name = "host_3"
    mock_host_3.status = "disabled"
    mock_host_a = NonCallableMock()
    mock_host_a.name = "host_a"
    mock_host_a.status = "disabled"
    mock_host_b = NonCallableMock()
    mock_host_b.name = "host_b"
    mock_host_b.status = "disabled"
    mock_host_alpha = NonCallableMock()
    mock_host_alpha.name = "host_alpha"
    mock_host_alpha.status = "enabled"
    mock_host_bar = NonCallableMock()
    mock_host_bar.name = "host_bar"
    mock_host_bar.status = "enabled"

    mock_conn.compute.aggregates.return_value = [mock_agg1, mock_agg2, mock_agg3]
    mock_conn.compute.hypervisors.return_value = [
        mock_host_0,
        mock_host_1,
        mock_host_2,
        mock_host_3,
        mock_host_a,
        mock_host_b,
        mock_host_alpha,
        mock_host_bar,
    ]

    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    res = hypervisor.get_aggregate_capacity()
    assert res == 0.5


@patch("apis.openstack_api.openstack_hypervisor.openstack.connect")
def test_get_aggregate_capacity_no_agg(mock_connect):
    """
    Docstring for test_get_aggregate_capacity
    """
    hypervisor_data = {
        "hypervisor_name": "host_a",
        "hypervisor_uptime_days": 123.0,
        "hypervisor_status": "enabled",
        "hypervisor_state": "up",
        "hypervisor_server_count": 10,
        "hypervisor_disabled_reason": None,
    }
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    mock_agg1 = NonCallableMock()
    mock_agg1.name = "agg1"
    mock_agg1.hosts = ["host_0", "host_1", "host_2", "host_3"]

    hypervisor = Hypervisor.from_dict("dev", hypervisor_data)

    with pytest.raises(ValueError):
        hypervisor.get_aggregate_capacity()


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

    res = get_available_flavors(mock_conn, "hvxyz.nubes.rl.ac.uk")

    mock_conn.compute.aggregates.assert_called_once()

    mock_aggregate_1.metadata.get.assert_any_call("hosttype")
    mock_aggregate_1.metadata.get.assert_any_call("local-storage-type")
    mock_aggregate_2.metadata.get.assert_any_call("hosttype")
    mock_aggregate_2.metadata.get.assert_any_call("local-storage-type")

    assert mock_aggregate_1.metadata.get.call_count == 2
    assert mock_aggregate_2.metadata.get.call_count == 2

    mock_conn.compute.flavors.assert_called_once()

    assert res == [mock_flavor_1.name, mock_flavor_2.name]
