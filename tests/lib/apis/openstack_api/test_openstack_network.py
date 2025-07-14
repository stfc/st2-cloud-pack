from unittest.mock import MagicMock, NonCallableMock, call
import pytest

from apis.openstack_api.enums.network_providers import NetworkProviders
from apis.openstack_api.enums.rbac_network_actions import RbacNetworkActions
from apis.openstack_api.openstack_network import (
    allocate_floating_ips,
    create_network,
    delete_network,
    create_network_rbac,
)

from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from apis.openstack_api.structs.network_details import NetworkDetails
from apis.openstack_api.structs.network_rbac import NetworkRbac


def test_allocate_floating_ip_project_not_found():
    """
    Tests that allocating a floating IP will raise if the project was not found
    """
    mock_project_identifier = "  "
    mock_network_identifier = NonCallableMock()
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        allocate_floating_ips(
            mock_conn, mock_network_identifier, mock_project_identifier, 10
        )
    mock_conn.network.create_ip.assert_not_called()


def test_allocate_floating_ip_network_not_found():
    """
    Tests that allocating a floating IP will raise if the network was not found
    """
    mock_project_identifier = NonCallableMock()
    mock_network_identifier = "   "
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        allocate_floating_ips(
            mock_conn, mock_network_identifier, mock_project_identifier, 10
        )
    mock_conn.network.create_ip.assert_not_called()


def test_allocate_floating_ip_zero_ips():
    """
    Tests allocate floating IP does not make any calls when 0 is passed
    """
    mock_project_identifier = "foo"
    mock_network_identifier = "bar  "
    mock_conn = MagicMock()
    res = allocate_floating_ips(
        mock_conn, mock_network_identifier, mock_project_identifier, 0
    )

    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.network.find_network.assert_called_once_with("bar", ignore_missing=False)
    mock_conn.network.create_ip.assert_not_called()
    assert res == []


@pytest.fixture(name="run_allocate_floating_ip_success")
def run_allocate_floating_ip_success_test():
    """fixture for testing successful allocation for one or more floating ip(s)"""

    def _run_internal(number_to_create, expected_calls):
        """
        internal test function
        :param number_to_create: number of floating ips to create
        :param expected_calls: number of times create_ip is expected to be called
        """
        mock_project_identifier = "foo"
        mock_network_identifier = "bar  "
        mock_conn = MagicMock()
        mock_conn.network.create_ip.side_effect = list(range(expected_calls))
        res = allocate_floating_ips(
            mock_conn,
            mock_network_identifier,
            mock_project_identifier,
            number_to_create,
        )

        mock_conn.identity.find_project.assert_called_once_with(
            "foo", ignore_missing=False
        )
        mock_conn.network.find_network.assert_called_once_with(
            "bar", ignore_missing=False
        )
        mock_conn.network.create_ip.assert_has_calls(
            [
                call(
                    project_id=mock_conn.identity.find_project.return_value.id,
                    floating_network_id=mock_conn.network.find_network.return_value.id,
                )
                for _ in range(expected_calls)
            ]
        )
        assert res == list(range(expected_calls))

    return _run_internal


def test_allocate_floating_ip_single_ip(run_allocate_floating_ip_success):
    """
    Tests allocate floating IP makes a single call to create IP
    """
    run_allocate_floating_ip_success(number_to_create=1, expected_calls=1)


def test_allocate_floating_ip_multiple_ips(run_allocate_floating_ip_success):
    """
    Tests allocating multiple IPs makes the correct number of queries
    """
    run_allocate_floating_ip_success(number_to_create=10, expected_calls=10)


def test_create_network_no_name():
    """
    Tests that create network with no new network name throws
    """
    mock_details = NetworkDetails(
        # name empty
        name="  ",
        description="",
        project_identifier="foo",
        provider_network_type=NetworkProviders.VXLAN,
        port_security_enabled=True,
        has_external_router=True,
    )
    mock_conn = MagicMock()

    with pytest.raises(MissingMandatoryParamError):
        create_network(mock_conn, mock_details)
    mock_conn.network.create_network.assert_not_called()


def test_create_network_missing_project():
    """
    Tests that create network with no project throws
    """
    mock_details = NetworkDetails(
        name="foo",
        description="",
        project_identifier="  ",
        provider_network_type=NetworkProviders.VXLAN,
        port_security_enabled=True,
        has_external_router=True,
    )
    mock_conn = MagicMock()

    with pytest.raises(MissingMandatoryParamError):
        create_network(mock_conn, mock_details)
    mock_conn.network.create_network.assert_not_called()


def test_create_network_success():
    """
    Tests that create network succeeds when provided valid inputs
    """
    mock_details = NetworkDetails(
        name="foo",
        description="bar",
        project_identifier="baz",
        provider_network_type=NetworkProviders.VXLAN,
        port_security_enabled=True,
        has_external_router=True,
    )
    mock_conn = MagicMock()
    res = create_network(mock_conn, mock_details)

    mock_conn.identity.find_project.assert_called_once_with("baz", ignore_missing=False)

    mock_conn.network.create_network.assert_called_once_with(
        project_id=mock_conn.identity.find_project.return_value.id,
        name="foo",
        description="bar",
        provider_network_type="vxlan",
        is_port_security_enabled=True,
        is_router_external=True,
    )

    assert res == mock_conn.network.create_network.return_value


def test_delete_network_not_found():
    """
    Tests that delete network will throw if a network isn't found
    """
    mock_network_identifier = "   "
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        delete_network(
            mock_conn,
            mock_network_identifier,
        )
    mock_conn.network.delete_network.assert_not_called()


def test_delete_network_success():
    """
    Tests that delete network succeeds with valid inputs
    """
    mock_network_identifier = "foo  "
    mock_conn = MagicMock()
    mock_conn.network.delete_network.return_value = None
    res = delete_network(
        mock_conn,
        mock_network_identifier,
    )
    mock_conn.network.find_network.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.network.delete_network.assert_called_once_with(
        mock_conn.network.find_network.return_value, ignore_missing=False
    )
    assert res


def test_create_network_rbac_network_missing():
    """
    Tests that create RBAC (network) will throw if a network param missing
    """
    mock_rbac_details = NetworkRbac(
        network_identifier="  ",
        project_identifier="foo",
        name="bar",
        action=RbacNetworkActions.SHARED,
    )
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_network_rbac(mock_conn, mock_rbac_details)
    mock_conn.network.create_rbac_policy.assert_not_called()


def test_create_network_rbac_project_not_found():
    """
    Tests that create RBAC (network) will throw if a project isn't found
    """
    mock_rbac_details = NetworkRbac(
        network_identifier="foo",
        project_identifier="  ",
        name="bar",
        action=RbacNetworkActions.SHARED,
    )
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_network_rbac(mock_conn, mock_rbac_details)
    mock_conn.network.create_rbac_policy.assert_not_called()


@pytest.mark.parametrize(
    "action_enum, expected_action_string",
    [
        (RbacNetworkActions.SHARED, "access_as_shared"),
        (RbacNetworkActions.EXTERNAL, "access_as_external"),
    ],
)
def test_create_network_rbac_success(action_enum, expected_action_string):
    """
    Tests that create RBAC (netowrk) succeeds when provided valid inputs
    """
    mock_rbac_details = NetworkRbac(
        network_identifier="foo",
        project_identifier="bar",
        name="baz",
        action=action_enum,
    )
    mock_conn = MagicMock()
    res = create_network_rbac(mock_conn, mock_rbac_details)

    mock_conn.network.find_network.assert_called_once_with("foo", ignore_missing=False)

    mock_conn.identity.find_project.assert_called_once_with("bar", ignore_missing=False)

    mock_conn.network.create_rbac_policy.assert_called_once_with(
        object_id=mock_conn.network.find_network.return_value.id,
        object_type="network",
        target_project_id=mock_conn.identity.find_project.return_value.id,
        action=expected_action_string,
    )

    assert res == mock_conn.network.create_rbac_policy.return_value


def test_create_rbac_unknown_key():
    """
    Tests a key error is thrown in an unknown var is passed to the serialisation logic
    """
    mock_rbac_details = NetworkRbac(
        network_identifier="foo",
        project_identifier="bar",
        name="baz",
        action="invalid-enum",
    )
    mock_conn = MagicMock()

    with pytest.raises(KeyError):
        create_network_rbac(mock_conn, mock_rbac_details)

    mock_conn.network.create_rbac_policy.assert_not_called()
