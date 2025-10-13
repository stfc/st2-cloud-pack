from unittest.mock import MagicMock, patch

import pytest

from workflows.icinga_search import (
    create_join_filter_functions,
    create_property_filter_functions,
    generate_table,
    search_by_name,
    search_by_state,
)


@pytest.fixture(name="mock_data")
def mock_data_fixture():
    """
    mock data returned from a query
    """
    return {
        "results": [
            {
                "attrs": {"handled": False, "name": "ping6", "state": 3},
                "joins": {"host": {"name": "Host1", "state": 1}},
                "meta": {},
                "name": "icinga2!ping6",
                "type": "Service",
            },
            {
                "attrs": {"handled": False, "name": "disk /", "state": 1},
                "joins": {"host": {"name": "Host2", "state": 0}},
                "meta": {},
                "name": "icinga2!disk /",
                "type": "Service",
            },
        ]
    }


expected = {
    "tabular_data": [["ping6", "UNKOWN"], ["disk /", "WARNING"]],
    "headers": ["Service Name", "Service State"],
}

expected_with_joins = {
    "tabular_data": [
        ["ping6", "UNKOWN", "Host1", "DOWN"],
        ["disk /", "WARNING", "Host2", "UP"],
    ],
    "headers": ["Service Name", "Service State", "Host Name", "Host State"],
}


@patch("workflows.icinga_search.tabulate")
@patch("workflows.icinga_search.json.loads")
@patch("workflows.icinga_search.query_object")
@pytest.mark.parametrize(
    "joins, expected",
    [
        ([], Expected),
        (["host.name", "host.state"], Expected_with_joins),
    ],
)
def test_search_by_state_success(
    mock_query_object,
    mock_json_loads,
    mock_tabulate,
    mock_data,
    joins,
    expected,
):
    """
    Tests search by state succeeds when providing joins and without joins
    """
    icinga_account = MagicMock()

    mock_query_object.return_value = [200, MagicMock()]
    mock_json_loads.return_value = mock_data

    search_by_state(
        icinga_account,
        object_type="Service",
        state="Critical",
        properties_to_select=["name", "state"],
        output_type="table",
        joins=joins,
    )

    mock_query_object.assert_called_once()

    mock_tabulate.assert_called_once_with(
        tabular_data=expected["tabular_data"],
        headers=expected["headers"],
        tablefmt="grid",
    )


@patch("workflows.icinga_search.tabulate")
@patch("workflows.icinga_search.json.loads")
@patch("workflows.icinga_search.query_object")
@pytest.mark.parametrize(
    "joins, expected",
    [
        ([], Expected),
        (["host.name", "host.state"], Expected_with_joins),
    ],
)
def test_search_by_name_success(
    mock_query_object,
    mock_json_loads,
    mock_tabulate,
    mock_data,
    joins,
    expected,
):
    """
    Tests search by name succeeds when providing joins and without joins
    """
    icinga_account = MagicMock()

    mock_query_object.return_value = [200, MagicMock()]
    mock_json_loads.return_value = mock_data

    search_by_name(
        icinga_account,
        object_type="Service",
        name="ping*",
        properties_to_select=["name", "state"],
        output_type="table",
        joins=joins,
    )

    mock_query_object.assert_called_once()

    mock_tabulate.assert_called_once_with(
        tabular_data=expected["tabular_data"],
        headers=expected["headers"],
        tablefmt="grid",
    )


def test_create_join_filter_functions():
    """
    Tests that join_filter_functions return the correcy keys from a dictionary
    """
    mock_user_joins = ["host.name", "host.state"]
    mock_data = {"joins": {"host": {"name": "Host2", "state": 0}}}

    filter_functions = create_join_filter_functions(mock_user_joins)

    expected = ["Host2", "UP"]

    for idx, fn in enumerate(filter_functions):
        assert fn(mock_data) == expected[idx]


def test_create_properties_filter_functions():
    """
    Tests that properties_filter_functions return the correcy keys from a dictionary
    """
    mock_user_properties = ["name", "state"]
    mock_data = {"attrs": {"handled": False, "name": "ping6", "state": 3}}

    filter_functions = create_property_filter_functions("Service", mock_user_properties)

    expected = ["ping6", "UNKOWN"]

    for idx, fn in enumerate(filter_functions):
        assert fn(mock_data) == expected[idx]


@patch("workflows.icinga_search.tabulate")
@patch("workflows.icinga_search.create_join_filter_functions")
@patch("workflows.icinga_search.create_property_filter_functions")
def test_generate_table(
    mock_create_property_filter_functions,
    mock_create_joins_filter_functions,
    mock_tabulate,
    mock_data,
):
    """
    tests that generate_table creates filter functions and creates a tabulate table
    """
    mock_user_properties = ["name", "state"]
    mock_user_joins = ["host.name", "host.state"]

    generate_table(mock_data, "Service", mock_user_properties, mock_user_joins)

    mock_create_property_filter_functions.assert_called_once_with(
        "Service", mock_user_properties
    )
    mock_create_joins_filter_functions.assert_called_once_with(mock_user_joins)

    mock_tabulate.assert_called_once()
