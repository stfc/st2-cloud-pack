from unittest.mock import MagicMock, patch
import pytest
import ipaddress
from openstack_api.openstack_subnet import create_subnet
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from exceptions.item_not_found_error import ItemNotFoundError


def test_create_subnet_network_missing():
    """
    Tests that create subnet throws if the network specified is missing
    """
    mock_network_identifier = "  "
    mock_subnet_name = "foo"
    mock_subnet_description = ""
    mock_dhcp_enabled = False

    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_subnet(
            mock_conn,
            mock_network_identifier,
            mock_subnet_name,
            mock_subnet_description,
            mock_dhcp_enabled,
        )
    mock_conn.network.create_subnet.assert_not_called()


def test_create_subnet_name_missing():
    """
    Tests that create subnet throws if the subnet name specified is missing
    """
    mock_network_identifier = "foo"
    mock_subnet_name = "  "
    mock_subnet_description = ""
    mock_dhcp_enabled = False

    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_subnet(
            mock_conn,
            mock_network_identifier,
            mock_subnet_name,
            mock_subnet_description,
            mock_dhcp_enabled,
        )
    mock_conn.network.create_subnet.assert_not_called()


def test_create_subnet_no_available_subnets():
    """
    Tests that create subnet throws error handles empty network
    """
    mock_network_identifier = "foo"
    mock_subnet_name = "bar"
    mock_subnet_description = "baz"
    mock_dhcp_enabled = False
    mock_conn = MagicMock()

    # Create 254 mock subnets to simulate all subnets being used
    mock_subnets = [MagicMock() for _ in range(254)]
    for i, subnet in enumerate(mock_subnets, start=1):
        subnet.gateway_ip = f"192.168.{i}.1"
    mock_conn.network.subnets.return_value = mock_subnets

    with pytest.raises(ItemNotFoundError):
        create_subnet(
            mock_conn,
            mock_network_identifier,
            mock_subnet_name,
            mock_subnet_description,
            mock_dhcp_enabled,
        )
    mock_conn.network.create_subnet.assert_not_called()


def test_create_subnet_success():
    """
    Tests create subnet creates a subnet
    """
    mock_network_identifier = "foo"
    mock_subnet_name = "bar"
    mock_subnet_description = "baz"
    mock_dhcp_enabled = False
    mock_conn = MagicMock()
    mock_conn.network.subnets.return_value = []  # mock all available

    mock_subnet_choice = ipaddress.ip_network("192.168.2.0/24")
    mock_hosts = [str(i) for i in mock_subnet_choice.hosts()]

    with patch("random.choice") as mock_choice:
        mock_choice.return_value = mock_subnet_choice
        res = create_subnet(
            mock_conn,
            mock_network_identifier,
            mock_subnet_name,
            mock_subnet_description,
            mock_dhcp_enabled,
        )

    mock_conn.network.find_network.assert_called_once_with(
        mock_network_identifier, ignore_missing=False
    )
    mock_conn.network.subnets.assert_called_once_with(
        network_id=mock_conn.network.find_network.return_value.id
    )
    mock_conn.network.create_subnet.assert_called_once_with(
        ip_version=4,
        network_id=mock_conn.network.find_network.return_value.id,
        allocation_pools=[{"start": mock_hosts[10], "end": mock_hosts[-1]}],
        cidr=str(mock_subnet_choice),
        gateway_ip=mock_hosts[0],
        name="bar",
        description="baz",
        is_dhcp_enabled=False,
    )

    assert res == mock_conn.network.create_subnet.return_value
