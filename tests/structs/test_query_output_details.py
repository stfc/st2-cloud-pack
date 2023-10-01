import pytest
from structs.query.query_output_details import QueryOutputDetails
from enums.query.props.server_properties import ServerProperties
from enums.query.query_output_types import QueryOutputTypes


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance to run tests with
    """
    return QueryOutputDetails


@pytest.fixture(name="run_kwargs_test_case")
def run_kwargs_test_case_fixture(instance):
    """
    Fixture runs a test case with different kwargs
    """

    def _run_from_kwargs_case(kwargs):
        """
        Helper function for running from_kwargs test cases
        """
        return instance.from_kwargs(prop_cls=ServerProperties, **kwargs)

    return _run_from_kwargs_case


def test_from_kwargs_none_given(run_kwargs_test_case):
    """
    tests that from_kwargs static method works expectedly - no kwargs given
    method should create a QueryOutputDetails with default params
    """
    res = run_kwargs_test_case({})
    assert res.properties_to_select == list(ServerProperties)
    assert res.output_type == QueryOutputTypes.TO_STR
    assert not res.group_by
    assert not res.sort_by
    assert not res.group_ranges
    assert not res.include_ungrouped_results


def test_from_kwargs_props_given(run_kwargs_test_case):
    """
    tests that from_kwargs static method works expectedly - props given
    method should create a QueryOutputDetails with props set
    """
    res = run_kwargs_test_case({"properties_to_select": ["server_id", "server_name"]})
    assert res.properties_to_select == [
        ServerProperties.SERVER_ID,
        ServerProperties.SERVER_NAME,
    ]


def test_from_kwargs_output_type_given(run_kwargs_test_case):
    """
    tests that from_kwargs static method works expectedly - output type given
    method should create a QueryOutputDetails with output type set
    """
    res = run_kwargs_test_case({"output_type": "TO_LIST"})
    assert res.output_type == QueryOutputTypes.TO_LIST


def test_from_kwargs_group_by_given(run_kwargs_test_case):
    """
    tests that from_kwargs static method works expectedly - group by given
    method should create a QueryOutputDetails with group by set
    """
    res = run_kwargs_test_case({"group_by": "server_name"})
    assert res.group_by == ServerProperties.SERVER_NAME


def test_from_kwargs_sort_by_given(run_kwargs_test_case):
    """
    tests that from_kwargs static method works expectedly - sort by given
    method should create a QueryOutputDetails with sort by set
    """
    res = run_kwargs_test_case({"sort_by": ["server_name", "server_id"]})
    assert res.sort_by == [
        (ServerProperties.SERVER_NAME, False),
        (ServerProperties.SERVER_ID, False),
    ]
