from unittest.mock import MagicMock, patch

import pytest
from workflows.find_reinstall_candidate_hypervisors import (
    find_reinstall_candidate_hypervisors,
)


@patch("workflows.find_reinstall_candidate_hypervisors.HypervisorQuery")
def test_find_reinstall_candidate_hypervisors(mock_hypervisor_query):
    """Test find_reinstall_candidate_hypervisors using only required strings"""
    mock_query = MagicMock()

    mock_hypervisor_query.return_value = mock_query

    mock_query.to_string.return_value = "mock_string"

    params = {
        "cloud_account": "test_cloud",
    }
    result = find_reinstall_candidate_hypervisors(**params)

    assert result == "mock_string"

    mock_query.select_all.assert_called_once()
    mock_query.where.assert_any_call(
        preset="MATCHES_REGEX",
        prop="ip",
        value=r"^172\.16\.(?:\d{1,3})\.(?:\d{1,3})$",
    )
    mock_query.run.assert_called_once_with("test_cloud")


@patch("workflows.find_reinstall_candidate_hypervisors.HypervisorQuery")
@pytest.mark.parametrize(
    "output_type", ["to_html", "to_string", "to_objects", "to_props"]
)
def test_find_reinstall_candidate_hypervisors_with_params(
    mock_hypervisor_query_class, output_type
):
    """Test find_reinstall_candidate_hypervisors with all parameters"""
    mock_query = MagicMock()

    mock_hypervisor_query_class.return_value = mock_query

    params = {
        "cloud_account": "test_cloud",
        "ip_regex": r"^10\.11\.(?:\d{1,3})\.(?:\d{1,3})$",
        "max_vcpus": 40,
        "max_vms": 30,
        "properties_to_select": ["name", "vcpus_used"],
        "exclude_hostnames": ["rtx4000", "a100", "-"],
        "sort_by": "vcpus_used",
        "sort_direction": "asc",
        "output_type": output_type,
    }

    result = find_reinstall_candidate_hypervisors(**params)

    mock_query.select.assert_called_once_with("name", "vcpus_used")
    mock_query.where.assert_any_call(
        preset="MATCHES_REGEX",
        prop="ip",
        value=params["ip_regex"],
    )
    mock_query.where.assert_any_call(
        preset="MATCHES_REGEX", prop="name", value=r"^(?!.*(rtx4000|a100|\-)).*$"
    )
    mock_query.where.assert_any_call(
        preset="LESS_THAN_OR_EQUAL_TO", prop="vcpus_used", value=params["max_vcpus"]
    )
    mock_query.where.assert_any_call(
        preset="LESS_THAN_OR_EQUAL_TO", prop="running_vms", value=params["max_vms"]
    )
    mock_query.sort_by.assert_called_once_with(("vcpus_used", "asc"))
    mock_query.run.assert_called_once_with("test_cloud")

    assert (
        result
        == {
            "to_html": mock_query.to_html.return_value,
            "to_string": mock_query.to_string.return_value,
            "to_objects": mock_query.to_objects.return_value,
            "to_props": mock_query.to_props.return_value,
        }[output_type]
    )
