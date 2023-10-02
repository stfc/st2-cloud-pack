from unittest.mock import MagicMock, NonCallableMock, patch
import pytest

from openstack_query.runners.user_runner import UserRunner
from openstack.identity.v3.user import User

from exceptions.parse_query_error import ParseQueryError
from exceptions.enum_mapping_error import EnumMappingError
from enums.user_domains import UserDomains

# pylint:disable=protected-access


@pytest.fixture(name="instance")
def instance_fixture(mock_connection):
    """
    Returns an instance to run tests with
    """
    mock_marker_prop_func = MagicMock()
    return UserRunner(
        marker_prop_func=mock_marker_prop_func, connection_cls=mock_connection
    )


@patch("openstack_query.runners.user_runner.UserRunner._get_user_domain")
def test_parse_meta_params_with_from_domain(
    mock_get_user_domain, instance, mock_openstack_connection
):
    """
    Tests _parse_meta_params method works expectedly - with valid from_domain argument
    method should get domain id from a UserDomain enum by calling get_user_domain
    """

    mock_domain_enum = UserDomains.DEFAULT
    mock_get_user_domain.return_value = "default-domain-id"

    res = instance._parse_meta_params(
        mock_openstack_connection, from_domain=mock_domain_enum
    )
    mock_get_user_domain.assert_called_once_with(
        mock_openstack_connection, mock_domain_enum
    )

    assert res == {"domain_id": "default-domain-id"}


@patch("openstack_query.runners.user_runner.UserRunner._run_paginated_query")
def test_run_query_with_meta_arg_domain_id_with_server_side_filters(
    mock_run_paginated_query, instance, mock_openstack_connection
):
    """
    Tests the _run_query method works expectedly - when meta arg domain id given
    method should:
        - update filter kwargs to include "domain_id": <domain id given>
        - run _run_paginated_query with updated filter_kwargs
    """

    mock_user_list = mock_run_paginated_query.return_value = [
        "user1",
        "user2",
        "user3",
    ]
    mock_filter_kwargs = {"arg1": "val1", "arg2": "val2"}
    mock_domain_id = "domain-id1"

    res = instance._run_query(
        mock_openstack_connection,
        filter_kwargs=mock_filter_kwargs,
        domain_id=mock_domain_id,
    )

    mock_run_paginated_query.assert_called_once_with(
        mock_openstack_connection.identity.users,
        {**{"domain_id": mock_domain_id}, **mock_filter_kwargs},
    )
    assert res == mock_user_list


@patch("openstack_query.runners.user_runner.UserRunner._run_paginated_query")
def test_run_query_with_meta_arg_domain_id_with_no_server_filters(
    mock_run_paginated_query, instance, mock_openstack_connection
):
    """
    Tests the _run_query method works expectedly with no server side filters
    """

    mock_user_list = mock_run_paginated_query.return_value = [
        "user1",
        "user2",
        "user3",
    ]
    mock_filter_kwargs = None
    mock_domain_id = "domain-id1"
    res = instance._run_query(
        mock_openstack_connection,
        filter_kwargs=mock_filter_kwargs,
        domain_id=mock_domain_id,
    )

    mock_run_paginated_query.assert_called_once_with(
        mock_openstack_connection.identity.users, {"domain_id": mock_domain_id}
    )
    assert res == mock_user_list


def test_run_query_domain_id_meta_arg_preset_duplication(
    instance, mock_openstack_connection
):
    """
    Tests that an error is raised when run_query is called with filter kwargs which contians domain_id and with meta
    params that also contains a domain id - i.e. there's a mismatch in which domain to search
    """
    with pytest.raises(ParseQueryError):
        instance._run_query(
            mock_openstack_connection,
            filter_kwargs={"domain_id": "some-domain"},
            domain_id=["some-other-domain"],
        )


@patch("openstack_query.runners.user_runner.UserRunner._run_paginated_query")
@patch("openstack_query.runners.user_runner.UserRunner._get_user_domain")
def test_run_query_no_meta_args(
    mock_get_user_domain, mock_run_paginated_query, instance, mock_openstack_connection
):
    """
    Tests that run_query functions expectedly - when no meta args given
    method should use the default-domain-id
    """
    mock_run_paginated_query.side_effect = [["user1", "user2"]]
    mock_get_user_domain.return_value = "default-domain-id"
    mock_filter_kwargs = {"test_arg": NonCallableMock()}

    res = instance._run_query(
        mock_openstack_connection, filter_kwargs=mock_filter_kwargs, domain_id=None
    )

    mock_get_user_domain.assert_called_once_with(
        mock_openstack_connection, instance.DEFAULT_DOMAIN
    )
    mock_run_paginated_query.asset_called_once_with(
        mock_openstack_connection.identity.users,
        {
            **mock_filter_kwargs,
            "all_tenants": True,
            "domain_id": "default-domain-id",
        },
    )
    assert res == ["user1", "user2"]


def test_run_query_returns_list(instance, mock_openstack_connection):
    """
    Tests that run_query correctly returns a list of entries
    """
    return_value = NonCallableMock()
    mock_openstack_connection.identity.find_user.return_value = return_value

    returned = instance._run_query(mock_openstack_connection, filter_kwargs={"id": "1"})
    assert [return_value] == returned


def test_run_query_with_from_domain_and_id_given(instance, mock_openstack_connection):
    """
    Test error is raised when the domain name and domain id is provided at
    the same time
    """
    with pytest.raises(ParseQueryError):
        instance._run_query(
            mock_openstack_connection,
            filter_kwargs={"domain_id": 1},
            domain_id="domain-id2",
        )


def test_get_user_domain(instance, mock_openstack_connection):
    """
    Test that user domains have a mapping and no errors are raised
    """
    for domain in UserDomains:
        instance._get_user_domain(mock_openstack_connection, domain)


def test_get_user_domain_error_raised(instance, mock_openstack_connection):
    """
    Test that an error is raised if a domain mapping is not found
    """
    with pytest.raises(EnumMappingError):
        instance._get_user_domain(mock_openstack_connection, MagicMock())


def test_parse_subset(instance, mock_openstack_connection):
    """
    Tests _parse_subset works expectedly
    method simply checks each value in 'subset' param is of the User type and returns it
    """

    # with one item
    mock_user_1 = MagicMock()
    mock_user_1.__class__ = User
    res = instance._parse_subset(mock_openstack_connection, [mock_user_1])
    assert res == [mock_user_1]

    # with two items
    mock_user_2 = MagicMock()
    mock_user_2.__class__ = User
    res = instance._parse_subset(mock_openstack_connection, [mock_user_1, mock_user_2])
    assert res == [mock_user_1, mock_user_2]


def test_parse_subset_invalid(instance, mock_openstack_connection):
    """
    Tests _parse_subset works expectedly
    method raises error when provided value which is not of User type
    """
    invalid_user = "invalid-user-obj"
    with pytest.raises(ParseQueryError):
        instance._parse_subset(mock_openstack_connection, [invalid_user])
