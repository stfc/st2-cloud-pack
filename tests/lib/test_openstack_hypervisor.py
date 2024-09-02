from unittest import mock

import pytest

from enums.query.props.hypervisor_properties import HypervisorProperties
from enums.query.query_presets import QueryPresetsGeneric
from openstack_api.openstack_hypervisor import OpenstackHypervisor
from openstack_query import HypervisorQuery


@pytest.fixture(name="mocked_query_factory")
def mocked_query_factory_fixture():
    """
    Returns a mock class for the query library
    """
    return mock.create_autospec(HypervisorQuery)


@pytest.fixture(name="openstack_hypervisor")
def openstack_hypervisor_fixture(mocked_query_factory):
    """
    Returns a pre-prepared OpenstackHypervisor object
    for testing on
    """
    return OpenstackHypervisor(query_class=mocked_query_factory)


def test_selected_type_with_invalid_type(openstack_hypervisor):
    """
    Tests that using an invalid search type raises a ValueError
    (this is from the user input layer)
    """
    with pytest.raises(ValueError):
        openstack_hypervisor.find_hypervisor(
            cloud_account="test", search_type="invalid"
        )


def test_selected_type_unknown_type(openstack_hypervisor):
    """
    Tests that a search type from the enum layer raises a NotImplementedError
    as it's likely the enum was updated without updating the selection
    """
    with mock.patch(
        "openstack_api.openstack_hypervisor._HypervisorSearchTypes"
    ) as mocked_search_types:
        mocked_search_types.__getitem__.return_value = "some enum key not covered"

        with pytest.raises(NotImplementedError):
            openstack_hypervisor.find_hypervisor(
                cloud_account="test", search_type="invalid"
            )


def test_with_empty_hvs(openstack_hypervisor, mocked_query_factory):
    """
    Tests that the query is correctly set up and run for empty hypervisors
    and a sorted list of results is returned
    """
    query_obj = mocked_query_factory.return_value
    fake_query_output = {"hypervisor_name": ["hypervisor3", "hypervisor1"]}
    query_obj.run.return_value.to_props.return_value = fake_query_output

    result = openstack_hypervisor.find_hypervisor(
        cloud_account="test", search_type="EMPTY_HVS"
    )
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
