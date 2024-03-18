from unittest.mock import call, patch
import pytest

from openstack_query.query_blocks.query_grouper import QueryGrouper
from enums.query.props.server_properties import ServerProperties

from exceptions.parse_query_error import ParseQueryError


from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance with mocked prop_enum_cls inject
    """
    mock_prop_enum_cls = MockProperties
    return QueryGrouper(prop_enum_cls=mock_prop_enum_cls)


@pytest.fixture(name="run_group_by_runner")
def run_group_by_runner_fixture(instance, mock_get_prop_mapping):
    """
    A fixture to test run_group_by method
    """

    def _run_group_by_runner(
        mock_group_by,
        mock_group_ranges,
        mock_include_missing,
        mock_obj_list,
        expected_out,
    ):
        """
        runs run_group_by method with different test arts
        """
        with patch.object(
            MockProperties, "get_prop_mapping", wraps=mock_get_prop_mapping
        ) as mock_get_prop_func:
            instance.parse_group_by(
                mock_group_by, mock_group_ranges, mock_include_missing
            )
            res = instance.run_group_by(mock_obj_list)
            if mock_include_missing:
                mock_get_prop_func.assert_has_calls(
                    [call(mock_group_by), call(mock_group_by)]
                )
            else:
                mock_get_prop_func.assert_called_once_with(mock_group_by)

        for key, vals in res.items():
            assert key in res.keys()
            assert expected_out[key] == [i.as_object() for i in vals]

    return _run_group_by_runner


def test_parse_group_by_invalid(instance):
    """
    Tests parse_group_by - when given an invalid group by prop
    """
    with pytest.raises(ParseQueryError):
        instance.parse_group_by(ServerProperties.SERVER_ID)


def test_parse_group_by_with_string_aliases(mock_results_container):
    """
    Tests parse_group_by accepts string aliases
    """
    mock_as_object_vals = [
        {"name": "a", "id": 1},
        {"name": "a", "id": 2},
        {"name": "b", "id": 3},
        {"name": "b", "id": 4},
    ]

    expected_out = {
        "a": [{"name": "a", "id": 1}, {"name": "a", "id": 2}],
        "b": [{"name": "b", "id": 3}, {"name": "b", "id": 4}],
    }

    mock_obj_list = mock_results_container(mock_as_object_vals)
    instance = QueryGrouper(prop_enum_cls=ServerProperties)
    instance.parse_group_by(ServerProperties.SERVER_NAME)
    res = instance.run_group_by(mock_obj_list)
    for key, vals in res.items():
        assert key in res.keys()
        assert expected_out[key] == [i.as_object() for i in vals]


def test_run_group_by_no_group_mappings(run_group_by_runner, mock_results_container):
    """
    Tests run_group_by when given no group mappings
    """
    mock_as_object_vals = [
        {"prop_1": "a", "prop_2": 1},
        {"prop_1": "a", "prop_2": 2},
        {"prop_1": "b", "prop_2": 3},
        {"prop_1": "b", "prop_2": 4},
    ]

    expected_out = {
        "a": [{"prop_1": "a", "prop_2": 1}, {"prop_1": "a", "prop_2": 2}],
        "b": [{"prop_1": "b", "prop_2": 3}, {"prop_1": "b", "prop_2": 4}],
    }

    mock_obj_list = mock_results_container(mock_as_object_vals)

    run_group_by_runner(MockProperties.PROP_1, None, False, mock_obj_list, expected_out)


def test_run_group_by_with_group_mappings(run_group_by_runner, mock_results_container):
    """
    Tests run_group_by when given group mappings
    """
    mock_as_object_vals = [
        {"prop_1": "a", "prop_2": 1},
        {"prop_1": "b", "prop_2": 2},
        {"prop_1": "c", "prop_2": 3},
        {"prop_1": "d", "prop_2": 4},
    ]

    mock_group_mappings = {"mapping_1": ["a", "c"], "mapping_2": ["b"]}

    expected_out = {
        "mapping_1": [{"prop_1": "a", "prop_2": 1}, {"prop_1": "c", "prop_2": 3}],
        "mapping_2": [{"prop_1": "b", "prop_2": 2}],
    }

    mock_obj_list = mock_results_container(mock_as_object_vals)

    run_group_by_runner(
        MockProperties.PROP_1, mock_group_mappings, False, mock_obj_list, expected_out
    )


def test_run_group_by_with_include_missing(run_group_by_runner, mock_results_container):
    """
    Tests run_group_by when given group mappings and include_missing=True
    """
    mock_as_object_vals = [
        {"prop_1": "a", "prop_2": 1},
        {"prop_1": "b", "prop_2": 2},
        {"prop_1": "c", "prop_2": 3},
        {"prop_1": "d", "prop_2": 4},
    ]

    mock_group_mappings = {
        "mapping_1": ["a", "c"],
        "mapping_2": ["b"],
    }

    expected_out = {
        "mapping_1": [{"prop_1": "a", "prop_2": 1}, {"prop_1": "c", "prop_2": 3}],
        "mapping_2": [{"prop_1": "b", "prop_2": 2}],
        "ungrouped results": [{"prop_1": "d", "prop_2": 4}],
    }

    mock_obj_list = mock_results_container(mock_as_object_vals)

    run_group_by_runner(
        MockProperties.PROP_1, mock_group_mappings, True, mock_obj_list, expected_out
    )
