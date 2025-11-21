from unittest.mock import MagicMock, patch

import pytest
from apis.openstack_query_api.hypervisor_queries import (
    query_hypervisor_state,
    find_down_hypervisors,
    find_disabled_hypervisors,
)


@patch("apis.openstack_query_api.hypervisor_queries.ServerQuery")
@patch("apis.openstack_query_api.hypervisor_queries.HypervisorQuery")
def test_query_hypervisor_state_basic_hv_info_and_server_count(
    mock_hv_query_cls,
    mock_server_query_cls,
):
    hv_instance = MagicMock()
    hv_instance.to_props.return_value = [
        {
            "hypervisor_name": "hv1",
            "hypervisor_state": "up",
            "hypervisor_status": "enabled",
            "hypervisor_uptime_days": 10,
            "disabled_reason": None,
        },
        {
            "hypervisor_name": "hv2",
            "hypervisor_state": "down",
            "hypervisor_status": "disabled",
            "hypervisor_uptime_days": 0,
            "disabled_reason": "maintenance",
        },
    ]
    hv_instance.where.return_value = None
    hv_instance.select.return_value = None
    hv_instance.run.return_value = None
    mock_hv_query_cls.return_value = hv_instance

    server_instance = MagicMock()
    server_instance.group_by.return_value = None
    server_instance.run.return_value = None
    server_instance.to_props.return_value = {"hv1": [{"id": "srv-1"}, {"id": "srv-2"}]}
    mock_server_query_cls.return_value = server_instance

    result = query_hypervisor_state("test-cloud")

    assert isinstance(result, list)
    assert len(result) == 2

    hv1 = next(item for item in result if item["hypervisor_name"] == "hv1")
    assert hv1["hypervisor_server_count"] == 2
    assert hv1["hypervisor_state"] == "up"

    hv2 = next(item for item in result if item["hypervisor_name"] == "hv2")
    assert hv2["hypervisor_server_count"] == 0
    assert hv2["disabled_reason"] == "maintenance"

    mock_hv_query_cls.assert_called_once()
    hv_instance.where.assert_called_once_with("regex", "hypervisor_name", value="hv*")
    hv_instance.select.assert_called_once_with(
        "hypervisor_name",
        "hypervisor_state",
        "hypervisor_status",
        "hypervisor_uptime_days",
        "disabled_reason",
    )
    hv_instance.run.assert_called_once_with(
        cloud_account="test-cloud", all_projects=True, as_admin=True
    )
    hv_instance.to_props.assert_called_once()

    mock_server_query_cls.assert_called_once()
    server_instance.group_by.assert_called_once_with("hypervisor_name")
    server_instance.run.assert_called_once_with(
        cloud_account="test-cloud", all_projects=True, as_admin=True
    )
    server_instance.to_props.assert_called_once()


@patch("apis.openstack_query_api.hypervisor_queries.ServerQuery")
@patch("apis.openstack_query_api.hypervisor_queries.HypervisorQuery")
def test_query_hypervisor_state_empty_hv_list(
    mock_hv_query_cls,
    mock_server_query_cls,
):
    hv_instance = MagicMock()
    hv_instance.where.return_value = None
    hv_instance.select.return_value = None
    hv_instance.run.return_value = None
    hv_instance.to_props.return_value = []
    mock_hv_query_cls.return_value = hv_instance

    server_instance = MagicMock()
    server_instance.group_by.return_value = None
    server_instance.run.return_value = None
    server_instance.to_props.return_value = {"hv1": [{"id": "srv-1"}]}
    mock_server_query_cls.return_value = server_instance

    result = query_hypervisor_state("test-cloud")

    assert result == []

    hv_instance.where.assert_called_once()
    hv_instance.select.assert_called_once()
    hv_instance.run.assert_called_once()
    hv_instance.to_props.assert_called_once()

    server_instance.group_by.assert_called_once()
    server_instance.run.assert_called_once()
    server_instance.to_props.assert_called_once()


@patch("apis.openstack_query_api.hypervisor_queries.ServerQuery")
@patch("apis.openstack_query_api.hypervisor_queries.HypervisorQuery")
def test_query_hypervisor_state_servers_missing_hv_key(
    mock_hv_query_cls,
    mock_server_query_cls,
):
    hv_instance = MagicMock()
    hv_instance.where.return_value = None
    hv_instance.select.return_value = None
    hv_instance.run.return_value = None
    hv_instance.to_props.return_value = [
        {
            "hypervisor_name": "orphan-hv",
            "hypervisor_state": "up",
            "hypervisor_status": "enabled",
            "hypervisor_uptime_days": 5,
            "disabled_reason": None,
        }
    ]
    mock_hv_query_cls.return_value = hv_instance

    server_instance = MagicMock()
    server_instance.group_by.return_value = None
    server_instance.run.return_value = None
    server_instance.to_props.return_value = {}
    mock_server_query_cls.return_value = server_instance

    result = query_hypervisor_state("test-cloud")

    assert len(result) == 1
    assert result[0]["hypervisor_server_count"] == 0

    hv_instance.to_props.assert_called_once()
    server_instance.to_props.assert_called_once()


@patch("apis.openstack_query_api.hypervisor_queries.HypervisorQuery")
def test_find_down_hypervisors_valid(mock_hypervisor_query):
    """
    Tests find_down_hypervisors() function
    """
    mock_hypervisor_query_obj = mock_hypervisor_query.return_value

    res = find_down_hypervisors("test-cloud-account")

    mock_hypervisor_query_obj.run.assert_called_once_with(
        "test-cloud-account",
    )
    mock_hypervisor_query_obj.select.assert_called_once_with(
        "hypervisor_id",
        "hypervisor_name",
        "hypervisor_state",
        "hypervisor_status",
    )
    mock_hypervisor_query_obj.to_props.assert_called_once()

    assert res == mock_hypervisor_query_obj


@patch("apis.openstack_query_api.hypervisor_queries.HypervisorQuery")
def test_find_down_hypervisors_no_hvs_found(mock_hypervisor_query):
    """
    Tests that find_down_hypervisors fails when provided
    """
    mock_hypervisor_query_obj = mock_hypervisor_query.return_value
    mock_hypervisor_query_obj.return_value = None

    mock_hypervisor_query_obj.run.assert_called_once_with(
        "test-cloud-account",
    )
    mock_hypervisor_query_obj.select.assert_called_once_with(
        "hypervisor_id",
        "hypervisor_name",
        "hypervisor_state",
        "hypervisor_status",
    )
    mock_hypervisor_query_obj.to_props.assert_called_once()


@patch("apis.openstack_query_api.hypervisor_queries.HypervisorQuery")
def test_find_disabled_hypervisors_valid(mock_hypervisor_query):
    """
    Tests find_down_hypervisors() function
    """
    mock_hypervisor_query_obj = mock_hypervisor_query.return_value

    res = find_disabled_hypervisors("test-cloud-account")

    mock_hypervisor_query_obj.run.assert_called_once_with(
        "test-cloud-account",
    )
    mock_hypervisor_query_obj.select.assert_called_once_with(
        "hypervisor_id",
        "hypervisor_name",
        "hypervisor_state",
        "hypervisor_status",
    )
    mock_hypervisor_query_obj.to_props.assert_called_once()

    assert res == mock_hypervisor_query_obj


@patch("apis.openstack_query_api.hypervisor_queries.HypervisorQuery")
def test_find_disabled_hypervisors_no_hvs_found(mock_hypervisor_query):
    """
    Tests that find_disabled_hypervisors fails when provided
    """
    mock_hypervisor_query_obj = mock_hypervisor_query.return_value
    mock_hypervisor_query_obj.to_props.return_value = None

    with pytest.raises(RuntimeError):
        find_disabled_hypervisors("test-cloud-account")

    mock_hypervisor_query_obj.run.assert_called_once_with(
        "test-cloud-account",
    )
    mock_hypervisor_query_obj.select.assert_called_once_with(
        "hypervisor_id",
        "hypervisor_name",
        "hypervisor_state",
        "hypervisor_status",
    )
    mock_hypervisor_query_obj.to_props.assert_called_once()
