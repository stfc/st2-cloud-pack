from unittest.mock import MagicMock, call, patch

import pytest
from workflows.find_reinstall_candidate_hypervisors import (
    find_reinstall_candidate_hypervisors,
)


@patch("workflows.find_reinstall_candidate_hypervisors.ServerQuery")
@patch("workflows.find_reinstall_candidate_hypervisors.HypervisorQuery")
def test_find_reinstall_candidate_hypervisors(
    mock_hypervisor_query_class, mock_server_query_class
):
    """Test find_reinstall_candidate_hypervisors using only required strings"""
    mock_hypervisor_query = MagicMock()
    mock_hypervisor_query_class.return_value = mock_hypervisor_query

    mock_hypervisor_query.to_string.return_value = "mock_string"

    mock_server_query = MagicMock()
    mock_server_query_class.return_value = mock_server_query

    params = {
        "cloud_account": "test_cloud",
        "ip_regex": r"^172\.16\.(?:\d{1,3})\.(?:\d{1,3})$",
    }
    result = find_reinstall_candidate_hypervisors(**params)

    print("Result: ", result)

    assert result == "mock_string"

    properties_to_select = [
        "id",
        "ip",
        "memory_free",
        "memory",
        "memory_used",
        "name",
        "state",
        "status",
        "vcpus",
        "vcpus_used",
        "disabled_reason",
    ]

    mock_hypervisor_query.select.assert_any_call(*properties_to_select)

    mock_hypervisor_query.where.assert_any_call(
        preset="MATCHES_REGEX",
        prop="ip",
        value=r"^172\.16\.(?:\d{1,3})\.(?:\d{1,3})$",
    )
    mock_hypervisor_query.run.assert_called_once_with("test_cloud")
    mock_hypervisor_query.where(preset="EQUAL_TO", prop="state", value="up")
    mock_hypervisor_query.where(preset="EQUAL_TO", prop="status", value="enabled")


@patch("workflows.find_reinstall_candidate_hypervisors.ServerQuery")
@patch("workflows.find_reinstall_candidate_hypervisors.HypervisorQuery")
@pytest.mark.parametrize(
    "output_type",
    ["to_html", "to_string", "to_objects", "to_props", "to_csv", "to_json"],
)
def test_find_reinstall_candidate_hypervisors_with_params(
    mock_hypervisor_query_class, mock_server_query_class, output_type
):
    """Test find_reinstall_candidate_hypervisors with all parameters"""
    mock_hypervisor_query = MagicMock()
    mock_server_query = MagicMock()

    mock_hypervisor_query_class.return_value = mock_hypervisor_query
    mock_server_query_class.return_value = mock_server_query

    params = {
        "cloud_account": "test_cloud",
        "ip_regex": r"^10\.11\.(?:\d{1,3})\.(?:\d{1,3})$",
        "max_vcpus": 40,
        "max_vms": 30,
        "include_down": True,
        "include_disabled": True,
        "exclude_hostnames": ["rtx4000", "a100", "-"],
        "sort_by": "vcpus_used",
        "sort_direction": "asc",
        "output_type": output_type,
    }

    result = find_reinstall_candidate_hypervisors(**params)

    mock_hypervisor_query.where.assert_any_call(
        preset="MATCHES_REGEX",
        prop="ip",
        value=params["ip_regex"],
    )
    mock_hypervisor_query.where.assert_any_call(
        preset="NOT_MATCHES_REGEX", prop="name", value=r".*(?:rtx4000|a100|\-)"
    )
    mock_hypervisor_query.where.assert_any_call(
        preset="LESS_THAN_OR_EQUAL_TO", prop="vcpus_used", value=params["max_vcpus"]
    )
    assert (
        call(preset="EQUAL_TO", prop="state", value="up")
        not in mock_hypervisor_query.where.call_args_list
    )
    assert (
        call(preset="EQUAL_TO", prop="status", value="enabled")
        not in mock_hypervisor_query.where.call_args_list
    )
    mock_hypervisor_query.sort_by.assert_called_once_with(("vcpus_used", "asc"))
    mock_hypervisor_query.run.assert_called_once_with("test_cloud")

    assert (
        result
        == {
            "to_html": mock_hypervisor_query.to_html.return_value,
            "to_string": mock_hypervisor_query.to_string.return_value,
            "to_objects": mock_hypervisor_query.to_objects.return_value,
            "to_props": mock_hypervisor_query.to_props.return_value,
            "to_csv": mock_hypervisor_query.to_csv.return_value,
            "to_json": mock_hypervisor_query.to_json.return_value,
        }[output_type]
    )


@pytest.mark.parametrize(
    "include_flavours, exclude_flavours, expected_allowed",
    [
        # Case 1: Only include_flavours
        (["small", "medium"], None, ["hv1", "hv2", "hv4"]),
        # Case 2: Only exclude_flavours
        (None, ["large"], ["hv1", "hv3"]),
        # Case 3: Both include/exclude flavours
        (["small", "medium"], ["large"], ["hv1"]),
    ],
)
@patch("workflows.find_reinstall_candidate_hypervisors.OpenstackConnection")
@patch("workflows.find_reinstall_candidate_hypervisors.get_available_flavors")
@patch("workflows.find_reinstall_candidate_hypervisors.ServerQuery")
@patch("workflows.find_reinstall_candidate_hypervisors.HypervisorQuery")
def test_include_and_exclude_flavours_combined(
    mock_hypervisor_query_class,
    mock_server_query_class,
    mock_get_flavors,
    mock_openstack_connection,
    include_flavours,
    exclude_flavours,
    expected_allowed,
):
    """Test find_reinstall_candidate_hypervisors with flavour filtering."""
    mock_hypervisor_query = MagicMock()
    mock_hypervisor_query_class.return_value = mock_hypervisor_query

    mock_hypervisor_query.to_props.return_value = {
        "hypervisor_name": ["hv1", "hv2", "hv3", "hv4"]
    }

    mock_server_query = MagicMock()
    mock_server_query_class.return_value = mock_server_query

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
        "ip_regex": r"^172\.16\.(?:\d{1,3})\.(?:\d{1,3})$",
        "include_flavours": include_flavours,
        "exclude_flavours": exclude_flavours,
    }

    _ = find_reinstall_candidate_hypervisors(**params)

    mock_hypervisor_query.where.assert_any_call(
        preset="ANY_IN", prop="name", value=expected_allowed
    )


# pylint: disable=protected-access
@patch("workflows.find_reinstall_candidate_hypervisors.ServerQuery")
@patch("workflows.find_reinstall_candidate_hypervisors.HypervisorQuery")
def test_running_vms_filter_and_sort(
    mock_hypervisor_query_class,
    mock_server_query_class,
):
    mock_hypervisor_query = MagicMock()
    mock_hypervisor_query_class.return_value = mock_hypervisor_query

    def make_hv_result(name):
        hv = MagicMock()
        hv.get_prop.return_value = name
        hv._prop_enum_cls.HYPERVISOR_NAME = "hypervisor_name"
        hv._forwarded_props = {}

        def update_forwarded_properties(data):
            hv._forwarded_props.update(data)

        hv.update_forwarded_properties.side_effect = update_forwarded_properties
        return hv

    hv_result1 = make_hv_result("hv1")
    hv_result2 = make_hv_result("hv2")
    hv_result3 = make_hv_result("hv3")

    mock_results_container = MagicMock()
    mock_results_container._results = [hv_result1, hv_result2, hv_result3]
    mock_results_container._parsed_results = []
    mock_hypervisor_query.results_container = mock_results_container

    # pylint:disable-next=unused-argument
    def run_side_effect(*args, **kwargs):
        mock_hypervisor_query.results_container._results = [
            hv_result1,
            hv_result2,
            hv_result3,
        ]

    mock_hypervisor_query.run.side_effect = run_side_effect

    mock_server_query = MagicMock()
    mock_server_query_class.return_value = mock_server_query
    mock_server_query.to_props.return_value = {
        "hv1": ["vm1", "vm2"],  # 2 VMs (should remain)
        "hv2": ["vm1"],  # 1 VM (should remain)
        "hv3": ["vm1", "vm2", "vm3"],  # 3 VMs (should be filtered out)
    }

    mock_hypervisor_query.to_string.return_value = "final_result"

    params = {
        "cloud_account": "test_cloud",
        "ip_regex": r"^172\.16\.\d+\.\d+$",
        "max_vms": 2,
        "sort_by": "running_vms",
        "sort_direction": "asc",
    }

    result = find_reinstall_candidate_hypervisors(**params)

    hv_result1.update_forwarded_properties.assert_called_once_with({"running_vms": 2})
    hv_result2.update_forwarded_properties.assert_called_once_with({"running_vms": 1})
    hv_result3.update_forwarded_properties.assert_called_once_with({"running_vms": 3})

    # We should only have two HVs, as one has 3 > 2 VMs
    # Then also check sort order
    final_results = mock_hypervisor_query.results_container._results
    assert len(final_results) == 2
    assert final_results[0] == hv_result2
    assert final_results[1] == hv_result1

    assert result == "final_result"
