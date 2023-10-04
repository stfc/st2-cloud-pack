from unittest.mock import MagicMock, patch
import pytest

from openstack_query.runners.flavor_runner import FlavorRunner
from openstack.compute.v2.flavor import Flavor
from exceptions.parse_query_error import ParseQueryError

# pylint:disable=protected-access


@pytest.fixture(name="instance")
def instance_fixture(mock_connection):
    """
    Returns an instance to run tests with
    """
    mock_marker_prop_func = MagicMock()
    return FlavorRunner(
        marker_prop_func=mock_marker_prop_func, connection_cls=mock_connection
    )


def test_parse_query_params_raise_error(instance, mock_openstack_connection):
    """
    tests that parse_query_params raises error - FlavorQuery accepts no meta-params currently
    """

    with pytest.raises(ParseQueryError):
        instance._parse_meta_params(
            mock_openstack_connection, **{"arg1": "val1", "arg2": "val2"}
        )


@patch("openstack_query.runners.flavor_runner.FlavorRunner._run_paginated_query")
def test_run_query_no_server_filters(
    mock_run_paginated_query, instance, mock_openstack_connection
):
    """
    Tests that _run_query method works expectedly with no server-side filters
    """
    mock_user_list = mock_run_paginated_query.return_value = [
        "flavor1",
        "flavor2",
        "flavor3",
    ]
    mock_filter_kwargs = None
    res = instance._run_query(
        mock_openstack_connection,
        filter_kwargs=mock_filter_kwargs,
    )

    mock_run_paginated_query.assert_called_once_with(
        mock_openstack_connection.compute.flavors, {"details": True}
    )
    assert res == mock_user_list


def test_parse_subset(instance, mock_openstack_connection):
    """
    Tests _parse_subset works expectedly
    method simply checks each value in 'subset' param is of the User type and returns it
    """

    # with one item
    mock_flavor_1 = MagicMock()
    mock_flavor_1.__class__ = Flavor
    res = instance._parse_subset(mock_openstack_connection, [mock_flavor_1])
    assert res == [mock_flavor_1]

    # with two items
    mock_flavor_2 = MagicMock()
    mock_flavor_2.__class__ = Flavor
    res = instance._parse_subset(
        mock_openstack_connection, [mock_flavor_1, mock_flavor_2]
    )
    assert res == [mock_flavor_1, mock_flavor_2]


def test_parse_subset_invalid(instance, mock_openstack_connection):
    """
    Tests _parse_subset works expectedly
    method raises error when provided value which is not of User type
    """
    invalid_flavor = "invalid-flavor-obj"
    with pytest.raises(ParseQueryError):
        instance._parse_subset(mock_openstack_connection, [invalid_flavor])
