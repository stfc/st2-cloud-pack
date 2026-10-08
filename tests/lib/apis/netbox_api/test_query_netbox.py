from unittest.mock import MagicMock, patch, call

import pytest
from black import PYTHON_CELL_MAGICS

from apis.netbox_api.query_netbox import get_devices_by_role


#make connection to netbox

#filter by role and status

#sort by firmware date and return 

#optional arg time delta

#optional arg between prod and staging

@patch("apis.netbox_api.query_netbox.pynetbox.api")
def test_get_prod_devices_by_role(mock_api):
    test_netbox_account = MagicMock()
    mock_device_quattor = [MagicMock(), MagicMock()]
    mock_device_kolla = [MagicMock(), MagicMock()]

    mock_api.return_value.dcim.devices.filter.side_effect = [mock_device_quattor,mock_device_kolla]

    result = get_devices_by_role(cloud="prod", status="active", netbox_account=test_netbox_account)

    calls = [call(role_id=75, status="active"), call(role_id=224, status="active")]
    mock_api.return_value.dcim.devices.filter.assert_has_calls(calls)

    assert result == mock_device_quattor + mock_device_kolla

#test case for status
@patch("apis.netbox_api.query_netbox.pynetbox.api")
def test_get_staging_devices_by_role(mock_api):
    test_netbox_account = MagicMock()
    mock_device_quattor = [MagicMock(), MagicMock()]
    mock_device_kolla = [MagicMock(), MagicMock()]

    mock_api.return_value.dcim.devices.filter.side_effect = [mock_device_quattor,mock_device_kolla]

    result = get_devices_by_role(cloud="staging", status="active", netbox_account=test_netbox_account)

    calls = [call(role_id=213, status="active"), call(role_id=225, status="active")]
    mock_api.return_value.dcim.devices.filter.assert_has_calls(calls)

    assert result == mock_device_quattor + mock_device_kolla

@patch("apis.netbox_api.query_netbox.pynetbox.api")
def test_get_all_devices_by_role(mock_api):
    test_netbox_account = MagicMock()

    mock_device_quattor_prod = [MagicMock(), MagicMock()]
    mock_device_kolla_prod = [MagicMock(), MagicMock()]
    mock_device_quattor_staging = [MagicMock(), MagicMock()]
    mock_device_kolla_staging = [MagicMock(), MagicMock()]


    mock_api.return_value.dcim.devices.filter.side_effect = [mock_device_quattor_prod,mock_device_kolla_prod,
                                                             mock_device_quattor_staging, mock_device_kolla_staging]

    result = get_devices_by_role(cloud="all", status="active", netbox_account=test_netbox_account)

    calls = [call(role_id=75, status="active"), call(role_id=224, status="active"),
             call(role_id=213, status="active"), call(role_id=225, status="active")]
    mock_api.return_value.dcim.devices.filter.assert_has_calls(calls)

    assert result == mock_device_quattor_prod + mock_device_kolla_prod + mock_device_quattor_staging + mock_device_kolla_staging


@patch("apis.netbox_api.query_netbox.pynetbox.api")
def test_get_devices_by_role_typo(mock_api):
    test_netbox_account = MagicMock()
    mock_device_quattor = [MagicMock(), MagicMock()]
    mock_device_kolla = [MagicMock(), MagicMock()]

    mock_api.return_value.dcim.devices.filter.side_effect = [mock_device_quattor,mock_device_kolla]

    with pytest.raises(ValueError):
        get_devices_by_role(cloud="stagging", status="active", netbox_account=test_netbox_account)


#need to get quattor and kolla