from unittest.mock import MagicMock, patch
import pytest
from workflows.query_netbox_for_hypervisor_firmware_date import (
    query_netbox_for_hypervisor_firmware_date,
)
from apis.netbox_api.query_netbox import (
    ALL_HV_SLUGS,
    PROD_HV_SLUGS,
    STAGING_HV_SLUGS,
)


@pytest.mark.parametrize(
    "environment, slugs",
    [
        ("prod", PROD_HV_SLUGS),
        ("staging", STAGING_HV_SLUGS),
    ],
)
@patch("apis.netbox_api.query_netbox.pynetbox")
def test_query_netbox_for_hypervisor_info_with_prod_staging(
    mock_pynetbox, environment, slugs
):
    """tests that when we provide a valid environment - we run netbox query with the appropriate slugs"""
    mock_nb = mock_pynetbox.api.return_value

    host1 = MagicMock()
    host1.name = "host1"
    host1.platform = "Rocky8"
    host1.status = "active"
    host1.custom_fields = {"firmware_last_update": "2024-11-08"}

    host2 = MagicMock()
    host2.name = "host2"
    host2.platform = "Rocky9"
    host2.status = "active"
    host2.custom_fields = {"firmware_last_update": "2025-11-08"}

    host3 = MagicMock()
    host3.name = "host3"
    host3.platform = "Rocky10"
    host3.status = "active"
    host3.custom_fields = {"firmware_last_update": "2026-11-08"}

    mock_nb.dcim.devices.filter.return_value = [host1, host2, host3]
    mock_netbox_account = MagicMock()
    mock_status = "active"

    result = query_netbox_for_hypervisor_firmware_date(
        mock_netbox_account, environment, mock_status
    )

    mock_nb.dcim.devices.filter.assert_called_once_with(
        role=slugs,
        status=mock_status,
    )

    assert result == [
        {
            "name": "host1",
            "platform": "Rocky8",
            "status": "active",
            "fw_date": "2024-11-08",
        },
        {
            "name": "host2",
            "platform": "Rocky9",
            "status": "active",
            "fw_date": "2025-11-08",
        },
        {
            "name": "host3",
            "platform": "Rocky10",
            "status": "active",
            "fw_date": "2026-11-08",
        },
    ]


@patch("apis.netbox_api.query_netbox.pynetbox")
def test_query_netbox_for_hypervisor_info_with_all_environments(mock_pynetbox):
    """tests that when we provide the 'all' environment - we run netbox query with the appropriate slugs"""
    mock_nb = mock_pynetbox.api.return_value
    environment_slugs = ALL_HV_SLUGS
    environment = "all"

    host1 = MagicMock()
    host1.name = "host1"
    host1.platform = "Rocky8"
    host1.status = "active"
    host1.custom_fields = {"firmware_last_update": "2024-11-08"}

    host2 = MagicMock()
    host2.name = "host2"
    host2.platform = "Rocky9"
    host2.status = "active"
    host2.custom_fields = {"firmware_last_update": "2025-11-08"}

    host3 = MagicMock()
    host3.name = "host3"
    host3.platform = "Rocky10"
    host3.status = "active"
    host3.custom_fields = {"firmware_last_update": "2026-11-08"}

    mock_nb.dcim.devices.filter.return_value = [host1, host2, host3]
    mock_netbox_account = MagicMock()
    mock_status = "active"

    result = query_netbox_for_hypervisor_firmware_date(
        mock_netbox_account, environment, mock_status
    )

    mock_nb.dcim.devices.filter.assert_called_once_with(
        role=environment_slugs,
        status=mock_status,
    )

    assert result == [
        {
            "name": "host1",
            "platform": "Rocky8",
            "status": "active",
            "fw_date": "2024-11-08",
        },
        {
            "name": "host2",
            "platform": "Rocky9",
            "status": "active",
            "fw_date": "2025-11-08",
        },
        {
            "name": "host3",
            "platform": "Rocky10",
            "status": "active",
            "fw_date": "2026-11-08",
        },
    ]


@patch("apis.netbox_api.query_netbox.pynetbox")
def test_invalid_environment_raises_value_error(mock_pynetbox):
    """tests that when we provide an invalid environment - we raise a ValueError"""
    mock_netbox_account = MagicMock()

    with pytest.raises(ValueError, match=r"Unsupported environment: 'Prodds'"):
        query_netbox_for_hypervisor_firmware_date(
            mock_netbox_account, "Prodds", "active"
        )

    mock_pynetbox.api.assert_not_called()


@patch("apis.netbox_api.query_netbox.pynetbox")
def test_no_matching_hypervisors_returns_empty_list(mock_pynetbox):
    """tests that when we provide a valid environment but nothing is returned from netbox - we return empty list"""
    mock_netbox_account = MagicMock()
    mock_nb = mock_pynetbox.api.return_value
    mock_nb.dcim.devices.filter.return_value = []

    result = query_netbox_for_hypervisor_firmware_date(
        mock_netbox_account, "prod", "active"
    )

    assert result == []
