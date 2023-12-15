from unittest.mock import MagicMock, NonCallableMock, patch
import pytest

from openstack_query.runners.user_runner import UserRunner

from exceptions.parse_query_error import ParseQueryError
from exceptions.enum_mapping_error import EnumMappingError
from enums.user_domains import UserDomains


@pytest.fixture(name="instance")
def instance_fixture(mock_marker_prop_func):
    """
    Returns an instance to run tests with
    """
    return UserRunner(marker_prop_func=mock_marker_prop_func)


@pytest.mark.parametrize(
    "domain_enum, expected_domain",
    [
        (UserDomains.DEFAULT, "default"),
        (UserDomains.STFC, "stfc"),
        (UserDomains.OPENID, "openid"),
    ],
)
def test_parse_meta_params_with_from_domain(domain_enum, expected_domain, instance):
    """
    Tests parse_meta_params with valid from_domain argument
    method should get domain id from a UserDomain enum by calling get_user_domain
    """
    mock_id = NonCallableMock()

    mock_domain = {"id": mock_id}
    mock_connection = MagicMock()

    mock_connection.identity.find_domain.return_value = mock_domain

    res = instance.parse_meta_params(mock_connection, from_domain=domain_enum)

    mock_connection.identity.find_domain.assert_called_once_with(expected_domain)
    assert res == {"domain_id": mock_id}


def test_parse_meta_params_with_invalid_from_domain(instance):
    """
    Tests parse_meta_params with invalid from_domain argument, should raise error
    """
    with pytest.raises(EnumMappingError):
        instance.parse_meta_params(NonCallableMock(), from_domain=MagicMock())


def test_parse_meta_params_no_from_domain(instance):
    """
    Tests parse_meta_params with no from_domain argument
    should return empty meta-params
    """
    assert instance.parse_meta_params(NonCallableMock()) == {}


@patch("openstack_query.runners.runner_utils.RunnerUtils.run_paginated_query")
def test_run_query_with_meta_arg_domain_id_with_server_side_filters(
    mock_run_paginated_query, instance, mock_marker_prop_func
):
    """
    Tests the run_query method works expectedly - when meta arg domain id given
    method should:
        - update filter kwargs to include "domain_id": <domain id given>
        - run _run_paginated_query with updated filter_kwargs
    """
    mock_connection = MagicMock()
    mock_user_list = mock_run_paginated_query.return_value = [
        "user1",
        "user2",
        "user3",
    ]
    mock_filter_kwargs = {"arg1": "val1", "arg2": "val2"}
    mock_domain_id = "domain-id1"

    res = instance.run_query(
        mock_connection,
        filter_kwargs=mock_filter_kwargs,
        domain_id=mock_domain_id,
    )

    mock_run_paginated_query.assert_called_once_with(
        mock_connection.identity.users,
        mock_marker_prop_func,
        {**{"domain_id": mock_domain_id}, **mock_filter_kwargs},
    )
    assert res == mock_user_list


@patch("openstack_query.runners.runner_utils.RunnerUtils.run_paginated_query")
def test_run_query_with_meta_arg_domain_id_with_no_server_filters(
    mock_run_paginated_query, instance, mock_marker_prop_func
):
    """
    Tests the run_query method works expectedly with no server side filters
    """

    mock_user_list = mock_run_paginated_query.return_value = [
        "user1",
        "user2",
        "user3",
    ]
    mock_connection = MagicMock()
    mock_filter_kwargs = None
    mock_domain_id = "domain-id1"
    res = instance.run_query(
        mock_connection,
        filter_kwargs=mock_filter_kwargs,
        domain_id=mock_domain_id,
    )

    mock_run_paginated_query.assert_called_once_with(
        mock_connection.identity.users,
        mock_marker_prop_func,
        {"domain_id": mock_domain_id},
    )
    assert res == mock_user_list


def test_run_query_domain_id_meta_arg_preset_duplication(instance):
    """
    Tests that an error is raised when run_query is called with filter kwargs which contians domain_id and with meta
    params that also contains a domain id - i.e. there's a mismatch in which domain to search
    """
    with pytest.raises(ParseQueryError):
        instance.run_query(
            NonCallableMock(),
            filter_kwargs={"domain_id": "some-domain"},
            domain_id=["some-other-domain"],
        )


@patch("openstack_query.runners.runner_utils.RunnerUtils.run_paginated_query")
def test_run_query_no_meta_args(mock_run_paginated_query, instance):
    """
    Tests that run_query functions expectedly - when no meta args given
    method should use the default-domain-id
    """
    mock_run_paginated_query.side_effect = [["user1", "user2"]]

    mock_default_domain_id = NonCallableMock()
    mock_connection = MagicMock()
    mock_domain = {"id": mock_default_domain_id}
    mock_connection.identity.find_domain.return_value = mock_domain

    mock_filter_kwargs = {"test_arg": NonCallableMock()}

    res = instance.run_query(
        mock_connection, filter_kwargs=mock_filter_kwargs, domain_id=None
    )

    # stfc is default domain
    mock_connection.identity.find_domain.assert_called_once_with("stfc")

    mock_run_paginated_query.asset_called_once_with(
        mock_connection.identity.users,
        {
            **mock_filter_kwargs,
            "all_tenants": True,
            "domain_id": "default-domain-id",
        },
    )
    assert res == ["user1", "user2"]


def test_run_query_returns_list(instance):
    """
    Tests that run_query correctly returns a list of entries
    """
    return_value = NonCallableMock()
    mock_connection = MagicMock()
    mock_connection.identity.find_user.return_value = return_value

    returned = instance.run_query(mock_connection, filter_kwargs={"id": "1"})
    mock_connection.identity.find_user.assert_called_once_with("1", ignore_missing=True)
    assert [return_value] == returned


def test_run_query_with_from_domain_and_id_given(instance):
    """
    Test error is raised when the domain name and domain id is provided at
    the same time
    """
    with pytest.raises(ParseQueryError):
        instance.run_query(
            NonCallableMock(),
            filter_kwargs={"domain_id": 1},
            domain_id="domain-id2",
        )


def test_get_user_domain_id(instance):
    """
    Test that user domains have a mapping and no errors are raised
    """
    mock_connection = MagicMock()
    mock_id = NonCallableMock()
    mock_connection.identity.find_domain.return_value = {"id": mock_id}

    for domain_enum in UserDomains:
        res = instance.parse_meta_params(mock_connection, from_domain=domain_enum)
        assert res == {"domain_id": mock_id}
