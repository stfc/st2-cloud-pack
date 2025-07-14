from unittest.mock import MagicMock, call, patch

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
    "output_type",
    ["to_html", "to_string", "to_objects", "to_props", "to_csv", "to_json"],
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
        preset="NOT_MATCHES_REGEX", prop="name", value=r".*(?:rtx4000|a100|\-)"
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
            "to_csv": mock_query.to_csv.return_value,
            "to_json": mock_query.to_json.return_value,
        }[output_type]
    )


@pytest.mark.parametrize(
    "include_flavours, exclude_flavours, properties_to_select, expected_allowed",
    [
        # Case 1: Only include_flavours, name not in props
        (["small", "medium"], None, ["vcpus_used"], ["hv1", "hv2", "hv4"]),
        # Case 2: Only exclude_flavours, name not in props
        (None, ["large"], ["vcpus_used"], ["hv1", "hv3"]),
        # Case 3: Both include/exclude flavours, name not in props
        (["small", "medium"], ["large"], ["vcpus_used"], ["hv1"]),
        # Case 4: include_flavours with 'name' already in props
        (["small", "medium"], None, ["name", "vcpus_used"], ["hv1", "hv2", "hv4"]),
    ],
)
@patch("workflows.find_reinstall_candidate_hypervisors.OpenstackConnection")
@patch("workflows.find_reinstall_candidate_hypervisors.get_available_flavors")
@patch("workflows.find_reinstall_candidate_hypervisors.HypervisorQuery")
def test_include_and_exclude_flavours_combined(
    mock_hypervisor_query_class,
    mock_get_flavors,
    mock_openstack_connection,
    include_flavours,
    exclude_flavours,
    properties_to_select,
    expected_allowed,
):
    """Test find_reinstall_candidate_hypervisors with flavour filtering."""
    mock_query = MagicMock()
    mock_hypervisor_query_class.return_value = mock_query

    mock_query.to_props.return_value = {"hypervisor_name": ["hv1", "hv2", "hv3", "hv4"]}

    flavors_per_hv = {
        "hv1": {"small", "medium"},
        "hv2": {"medium", "large"},
        "hv3": {"xlarge"},
        "hv4": {"small", "large"},
    }

    def side_effect(_, hv_name):
        return flavors_per_hv.get(hv_name)

    mock_get_flavors.side_effect = side_effect

    mock_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.return_value = mock_conn

    params = {
        "cloud_account": "test_cloud",
        "include_flavours": include_flavours,
        "exclude_flavours": exclude_flavours,
        "properties_to_select": properties_to_select,
    }

    _ = find_reinstall_candidate_hypervisors(**params)

    # hv1 supports small and medium, no excluded flavours → allowed
    # hv2 supports medium but also large → excluded
    # hv3 supports only xlarge → not included
    # hv4 supports small (included) but also large (excluded) → excluded
    mock_query.where.assert_any_call(
        preset="ANY_IN", prop="name", value=expected_allowed
    )
    if "name" not in properties_to_select:
        mock_query.select.assert_has_calls(
            [
                call(*properties_to_select),
                call("name", *properties_to_select),
                call(*properties_to_select),
            ],
            any_order=False,
        )
    else:
        mock_query.select.assert_called_once_with(*properties_to_select)
