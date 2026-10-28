from unittest.mock import MagicMock, patch
import pytest
from apis.netbox_api.query_netbox import (
    get_hypervisors_by_environment_and_status,
    ALL_HV_SLUGS,
    STAGING_HV_SLUGS,
    PROD_HV_SLUGS,
)


@patch("apis.netbox_api.query_netbox.pynetbox")
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
def test_get_hypervisors_by_environment_and_status_different_statuses(
    mock_pynetbox, status
):
    mock_netbox = MagicMock()
    mock_environment = "staging"
    expected_hypervisors = [MagicMock(), MagicMock(), MagicMock()]

    mock_nb = mock_pynetbox.api.return_value
    mock_nb.dcim.devices.filter.return_value = expected_hypervisors

    result = get_hypervisors_by_environment_and_status(
        mock_netbox, mock_environment, status
    )

    mock_nb.dcim.devices.filter.assert_called_once_with(
        role=STAGING_HV_SLUGS,
        status=status,
    )
    assert result == expected_hypervisors


@patch("apis.netbox_api.query_netbox.pynetbox")
@pytest.mark.parametrize("environment", ["prod", "staging", "all"])
def test_get_hypervisors_by_environment_and_status_different_environments(
    mock_pynetbox, environment
):
    expected_slugs = {
        "prod": PROD_HV_SLUGS,
        "staging": STAGING_HV_SLUGS,
        "all": ALL_HV_SLUGS,
    }[environment]
    expected_hypervisors = [MagicMock(), MagicMock(), MagicMock()]

    mock_nb = mock_pynetbox.api.return_value
    mock_nb.dcim.devices.filter.return_value = expected_hypervisors

    result = get_hypervisors_by_environment_and_status(
        MagicMock(), environment, "active"
    )

    mock_nb.dcim.devices.filter.assert_called_once_with(
        role=expected_slugs,
        status="active",
    )
    assert result == expected_hypervisors


@patch("apis.netbox_api.query_netbox.pynetbox")
def test_get_hypervisors_by_environment_and_any_status(mock_pynetbox):
    mock_netbox = MagicMock()
    mock_environment = "staging"
    mock_status = "any"
    expected_hypervisors = [MagicMock(), MagicMock(), MagicMock()]

    mock_nb = mock_pynetbox.api.return_value
    mock_nb.dcim.devices.filter.return_value = expected_hypervisors

    result = get_hypervisors_by_environment_and_status(
        mock_netbox, mock_environment, mock_status
    )

    mock_nb.dcim.devices.filter.assert_called_once_with(
        role=STAGING_HV_SLUGS,
    )

    assert result == expected_hypervisors


@patch("apis.netbox_api.query_netbox.pynetbox")
def test_get_hypervisors_by_environment_and_status_invalid_environment(
    mock_pynetbox,
):
    with pytest.raises(ValueError, match="Unsupported environment: 'invalid'"):
        get_hypervisors_by_environment_and_status(MagicMock(), "invalid", "active")

    mock_pynetbox.api.assert_not_called()
