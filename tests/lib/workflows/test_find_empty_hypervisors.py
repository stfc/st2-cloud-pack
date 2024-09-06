from unittest.mock import patch

from enums.query.props.hypervisor_properties import HypervisorProperties
from enums.query.query_presets import QueryPresetsGeneric
from workflows.find_empty_hypervisors import find_empty_hypervisors


@patch("workflows.find_empty_hypervisors.HypervisorQuery")
def test_with_empty_hvs(mocked_query_factory):
    """
    Tests that the query is correctly set up and run for empty hypervisors
    and a sorted list of results is returned
    """
    query_obj = mocked_query_factory.return_value
    fake_query_output = {"hypervisor_name": ["hypervisor3", "hypervisor1"]}
    query_obj.run.return_value.to_props.return_value = fake_query_output

    result = find_empty_hypervisors(cloud_account="test")
    mocked_query_factory.assert_called_once_with()

    query_obj.select.assert_called_once_with(HypervisorProperties.HYPERVISOR_NAME)
    query_obj.where.assert_called_once_with(
        QueryPresetsGeneric.EQUAL_TO,
        HypervisorProperties.HYPERVISOR_VCPUS_USED,
        value=0,
    )
    query_obj.run.assert_called_once_with(cloud_account="test")
    query_results = query_obj.run.return_value
    query_results.to_props.assert_called_once_with(flatten=True)

    assert result == sorted(query_results.to_props.return_value["hypervisor_name"])
