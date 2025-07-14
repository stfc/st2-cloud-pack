from unittest.mock import MagicMock
import pytest

from apis.openstack_api.openstack_router import (
    add_interface_to_router,
    check_for_internal_routers,
    create_router,
)
from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from apis.openstack_api.structs.router_details import RouterDetails


def test_add_interface_to_router_router_missing():
    """
    Tests that add interface to router will throw if the router
    is missing
    """
    mock_router_identifier = "  "
    mock_project_identifier = "foo"
    mock_subnet_identifier = "bar"
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        add_interface_to_router(
            mock_conn,
            mock_project_identifier,
            mock_router_identifier,
            mock_subnet_identifier,
        )
    mock_conn.network.add_interface_to_router.assert_not_called()


def test_add_interface_to_router_subnet_missing():
    """
    Tests that add interface to router will throw if the subnet
    is missing
    """
    mock_router_identifier = "foo"
    mock_project_identifier = "bar"
    mock_subnet_identifier = "   "
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        add_interface_to_router(
            mock_conn,
            mock_project_identifier,
            mock_router_identifier,
            mock_subnet_identifier,
        )
    mock_conn.network.add_interface_to_router.assert_not_called()


def test_add_interface_to_router_project_missing():
    """
    Tests that add interface to router will throw if the project
    is missing
    """
    mock_router_identifier = "foo"
    mock_project_identifier = "  "
    mock_subnet_identifier = "bar"
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        add_interface_to_router(
            mock_conn,
            mock_project_identifier,
            mock_router_identifier,
            mock_subnet_identifier,
        )
    mock_conn.network.add_interface_to_router.assert_not_called()


def test_add_interface_to_router_successful():
    """
    Tests that the correct call is made when add_interface is called
    """
    mock_router_identifier = "foo"
    mock_project_identifier = "bar"
    mock_subnet_identifier = "baz"
    mock_conn = MagicMock()
    res = add_interface_to_router(
        mock_conn,
        mock_project_identifier,
        mock_router_identifier,
        mock_subnet_identifier,
    )
    mock_conn.identity.find_project.assert_called_once_with("bar", ignore_missing=False)

    mock_conn.network.find_router.assert_called_once_with(
        "foo",
        project_id=mock_conn.identity.find_project.return_value.id,
        ignore_missing=False,
    )

    mock_conn.network.find_subnet.assert_called_once_with(
        "baz",
        project_id=mock_conn.identity.find_project.return_value.id,
        ignore_missing=False,
    )

    mock_conn.network.add_interface_to_router.assert_called_once_with(
        router=mock_conn.network.find_router.return_value,
        subnet_id=mock_conn.network.find_subnet.return_value.id,
    )

    assert res == mock_conn.network.find_router.return_value


def test_create_router_project_missing():
    """
    Tests that create router will throw if the project is missing
    """
    mock_details = RouterDetails(
        project_identifier=" ",
        router_name="foo",
        router_description="",
        external_gateway="bar",
        is_distributed=False,
    )
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_router(mock_conn, mock_details)
    mock_conn.network.create_router.assert_not_called()


def test_create_router_external_gateway_missing():
    """
    Tests that create router will throw if external external gateway is missing
    """
    mock_details = RouterDetails(
        project_identifier="foo",
        router_name="bar",
        router_description="",
        external_gateway="  ",
        is_distributed=False,
    )
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_router(mock_conn, mock_details)
    mock_conn.network.create_router.assert_not_called()


def test_create_router_name_not_given():
    """
    Tests that create router will throw if new router name was not given
    """
    mock_details = RouterDetails(
        project_identifier="foo",
        router_name=" ",
        router_description="",
        external_gateway="bar",
        is_distributed=False,
    )
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_router(mock_conn, mock_details)
    mock_conn.network.create_router.assert_not_called()


def test_create_router_successful():
    """
    Tests that create router succeeds when params valid
    """
    mock_details = RouterDetails(
        project_identifier="foo",
        router_name="bar",
        router_description="",
        external_gateway="baz",
        is_distributed=False,
    )
    mock_conn = MagicMock()
    res = create_router(mock_conn, mock_details)

    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.network.find_network.assert_called_once_with("baz", ignore_missing=False)

    mock_conn.network.create_router.assert_called_once_with(
        project_id=mock_conn.identity.find_project.return_value.id,
        name="bar",
        description="",
        external_gateway_info={
            "network_id": mock_conn.network.find_network.return_value.id
        },
        is_distributed=False,
        is_ha=True,
    )
    assert res == mock_conn.network.create_router.return_value


def test_check_internal_router_found():
    """
    Test router with addresses 172.16 are returned
    """
    mock_router_1 = MagicMock()
    mock_router_1.id = "xxx-yyy-zzz"
    mock_router_1.external_gateway_info = {
        "external_fixed_ips": [
            {"ip_address": "172.16.1.1"},
            {"ip_address": "10.10.1.1"},
        ]
    }
    mock_router_2 = MagicMock()
    mock_router_2.id = "aaa-bbb-ccc"
    mock_router_2.external_gateway_info = {
        "external_fixed_ips": [
            {"ip_address": "130.80.1.1"},
        ]
    }
    mock_conn = MagicMock()
    mock_conn.network.routers.return_value = [mock_router_1, mock_router_2]

    res = check_for_internal_routers(mock_conn)

    assert res == [mock_router_1]


def test_check_internal_router_not_found():
    """
    Test routers not starting 172.16 are not returned
    """
    mock_router_1 = MagicMock()
    mock_router_1.id = "xxx-yyy-zzz"
    mock_router_1.external_gateway_info = {
        "external_fixed_ips": [
            {"ip_address": "192.168.1.1"},
            {"ip_address": "10.10.1.1"},
        ]
    }
    mock_router_2 = MagicMock()
    mock_router_2.id = "aaa-bbb-ccc"
    mock_router_2.external_gateway_info = None
    mock_conn = MagicMock()
    mock_conn.network.routers.return_value = [mock_router_1, mock_router_2]

    res = check_for_internal_routers(mock_conn)

    assert res == []
