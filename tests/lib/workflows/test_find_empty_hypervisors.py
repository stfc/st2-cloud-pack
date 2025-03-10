from unittest.mock import patch

from workflows.find_empty_hypervisors import find_empty_hypervisors


@patch("workflows.find_empty_hypervisors.HypervisorQuery")
def test_with_empty_hvs(mocked_query_factory):
    """
    Tests that the query is correctly set up and run for empty hypervisors
    and a sorted list of results is returned
    """
    query_obj = mocked_query_factory.return_value
    fake_query_output = {"hypervisor_name": ["hypervisor3", "hypervisor1"]}
    query_obj.run.return_value.sort_by.return_value.to_props.return_value = (
        fake_query_output
    )

    result = find_empty_hypervisors(cloud_account="test", include_offline=True)
    mocked_query_factory.assert_called_once_with()

    query_obj.select.assert_called_once_with("hypervisor_name")
    query_obj.where.assert_called_once_with(
        "equal_to",
        "hypervisor_vcpus_used",
        value=0,
    )
    query_obj.run.assert_called_once_with(cloud_account="test")
    query_results = query_obj.run.return_value
    query_results.sort_by.assert_called_once_with(["hypervisor_name", "asc"])
    sort_by_chain = query_results.sort_by.return_value
    sort_by_chain.to_props.assert_called_once_with(flatten=True)

    assert result == fake_query_output["hypervisor_name"]


@patch("workflows.find_empty_hypervisors.HypervisorQuery")
def test_with_empty_hvs_excluding_offline(mocked_query_factory):
    """
    Tests that the query is correctly set up and run for empty hypervisors
    including the where clause to filter out un-contactable hypervisors
    """
    query_obj = mocked_query_factory.return_value
    find_empty_hypervisors(cloud_account="test", include_offline=False)

    mocked_query_factory.assert_called_once_with()
    query_obj.select.assert_called_once_with("hypervisor_name")
    query_obj.where.assert_any_call(
        "equal_to",
        "hypervisor_vcpus_used",
        value=0,
    )
    query_obj.where.assert_any_call(
        "equal_to",
        "hypervisor_state",
        value="up",
    )
