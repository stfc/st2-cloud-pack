from unittest.mock import MagicMock, patch, call
import pytest
from apis.netbox_api.query_netbox import (
    _get_hypervisors_by_status_and_platform,
    get_metadata_from_hypervisor,
)


@patch("apis.netbox_api.query_netbox.pynetbox.api")
def test__get_hypervisors_by_status_and_platform_passes_args_in_order(mock_api):
    """
    Test for args passed in the correct order
    """
    test_netbox_account = MagicMock()

    _get_hypervisors_by_status_and_platform(test_netbox_account, "prod", "active")

    mock_api.assert_called_once_with(
        test_netbox_account.netbox_endpoint,
        token=test_netbox_account.api_token,
    )


@patch("apis.netbox_api.query_netbox.pynetbox.api")
def test_get_prod_hypervisors_by_role(mock_api):
    """
    Test for only getting prod hypervisors
    """
    test_netbox_account = MagicMock()
    mock_device_quattor = [MagicMock(), MagicMock()]
    mock_device_kolla = [MagicMock(), MagicMock()]

    mock_api.return_value.dcim.devices.filter.side_effect = [
        mock_device_quattor,
        mock_device_kolla,
    ]

    result = _get_hypervisors_by_status_and_platform(
        cloud="prod", status="active", netbox_account=test_netbox_account
    )

    calls = [call(role_id=75, status="active"), call(role_id=224, status="active")]
    mock_api.return_value.dcim.devices.filter.assert_has_calls(calls)

    assert result == mock_device_quattor + mock_device_kolla


@patch("apis.netbox_api.query_netbox.pynetbox.api")
def test_get_staging_hypervisors_by_role(mock_api):
    """
    Test for only getting staging hypervisors
    """
    test_netbox_account = MagicMock()
    mock_device_quattor = [MagicMock(), MagicMock()]
    mock_device_kolla = [MagicMock(), MagicMock()]

    mock_api.return_value.dcim.devices.filter.side_effect = [
        mock_device_quattor,
        mock_device_kolla,
    ]

    result = _get_hypervisors_by_status_and_platform(
        cloud="staging", status="active", netbox_account=test_netbox_account
    )

    calls = [call(role_id=213, status="active"), call(role_id=225, status="active")]
    mock_api.return_value.dcim.devices.filter.assert_has_calls(calls)

    assert result == mock_device_quattor + mock_device_kolla


@patch("apis.netbox_api.query_netbox.pynetbox.api")
def test_get_all_hypervisors_by_role(mock_api):
    """
    Test for only getting all hypervisors
    """
    test_netbox_account = MagicMock()

    mock_device_quattor_prod = [MagicMock(), MagicMock()]
    mock_device_kolla_prod = [MagicMock(), MagicMock()]
    mock_device_quattor_staging = [MagicMock(), MagicMock()]
    mock_device_kolla_staging = [MagicMock(), MagicMock()]

    mock_api.return_value.dcim.devices.filter.side_effect = [
        mock_device_quattor_prod,
        mock_device_kolla_prod,
        mock_device_quattor_staging,
        mock_device_kolla_staging,
    ]

    result = _get_hypervisors_by_status_and_platform(
        cloud="all", status="active", netbox_account=test_netbox_account
    )

    calls = [
        call(role_id=75, status="active"),
        call(role_id=224, status="active"),
        call(role_id=213, status="active"),
        call(role_id=225, status="active"),
    ]
    mock_api.return_value.dcim.devices.filter.assert_has_calls(calls)

    assert (
        result
        == mock_device_quattor_prod
        + mock_device_kolla_prod
        + mock_device_quattor_staging
        + mock_device_kolla_staging
    )


@patch("apis.netbox_api.query_netbox.pynetbox.api")
def test__get_hypervisors_by_status_and_platform_typo(mock_api):
    """
    Test for getting correct error when giving a param a typo
    """
    test_netbox_account = MagicMock()
    mock_device_quattor = [MagicMock(), MagicMock()]
    mock_device_kolla = [MagicMock(), MagicMock()]

    mock_api.return_value.dcim.devices.filter.side_effect = [
        mock_device_quattor,
        mock_device_kolla,
    ]

    with pytest.raises(ValueError):
        _get_hypervisors_by_status_and_platform(
            cloud="stagging", status="active", netbox_account=test_netbox_account
        )


@patch("apis.netbox_api.query_netbox.pynetbox.api")
@pytest.mark.parametrize(
    "status",
    [
        "active",
        "offline",
        "planned",
        "staged",
        "failed",
        "inventory",
        "decommissioning",
    ],
)
def test__get_hypervisors_by_status_and_platform(mock_api, status):
    """
    Test for making sure all the statuses pass and give hypervisors correctly
    """
    test_netbox_account = MagicMock()
    mock_device_quattor = [MagicMock(), MagicMock()]
    mock_device_kolla = [MagicMock(), MagicMock()]

    mock_api.return_value.dcim.devices.filter.side_effect = [
        mock_device_quattor,
        mock_device_kolla,
    ]

    result = _get_hypervisors_by_status_and_platform(
        cloud="staging", status=status, netbox_account=test_netbox_account
    )

    calls = [call(role_id=213, status=status), call(role_id=225, status=status)]
    mock_api.return_value.dcim.devices.filter.assert_has_calls(calls)

    assert result == mock_device_quattor + mock_device_kolla


@patch("apis.netbox_api.query_netbox._get_hypervisors_by_status_and_platform")
def test_get_metadata_from_hypervisor(mock_get_hypervisors):
    """
    Test for getting the correct and outputting the metadata from hypervisors
    """
    host1 = MagicMock()
    host2 = MagicMock()
    host_list = [host1, host2]
    mock_get_hypervisors.return_value = host_list

    host1.name = "host1"
    host1.custom_fields = {"firmware_last_update": "2024-11-08"}
    host2.platform = "Rocky 8"
    host2.name = "host2"
    host2.custom_fields = {"firmware_last_update": None}
    host2.platform = "Rocky 9"

    hypervisor1 = {
        "name": host1.name,
        "platform": host1.platform,
        "fw_date": host1.custom_fields["firmware_last_update"],
    }
    hypervisor2 = {
        "name": host2.name,
        "platform": host2.platform,
        "fw_date": host2.custom_fields["firmware_last_update"],
    }

    hypervisor_dict_list = [hypervisor1, hypervisor2]

    test_netbox_account = MagicMock()
    res = get_metadata_from_hypervisor(test_netbox_account, "prod", "active")
    assert res == hypervisor_dict_list
