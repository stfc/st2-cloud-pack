from unittest.mock import patch, MagicMock
from apis.openstack_api.structs.quota_details import QuotaDetails
from workflows.quota_actions import quota_set


@patch("workflows.quota_actions.openstack_quota.set_quota")
def test_quota_set(mock_api_set_quota):
    """
    Tests that quota_set function forwards on request to openstack API set_quota function
    and returns the correct status (True)
    """

    # setup input values
    mock_conn = MagicMock()
    mock_project_identifier = "project-id"
    mock_floating_ips = 1
    mock_security_group_rules = 1
    mock_cores = 1
    mock_gigabytes = 1
    mock_instances = 1
    mock_backups = 1
    mock_ram = 1
    mock_security_groups = 1
    mock_snapshots = 1
    mock_volumes = 1

    status = quota_set(
        mock_conn,
        mock_project_identifier,
        mock_floating_ips,
        mock_security_group_rules,
        mock_cores,
        mock_gigabytes,
        mock_instances,
        mock_backups,
        mock_ram,
        mock_security_groups,
        mock_snapshots,
        mock_volumes,
    )

    mock_api_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            mock_project_identifier,
            mock_floating_ips,
            mock_security_group_rules,
            mock_cores,
            mock_gigabytes,
            mock_instances,
            mock_backups,
            mock_ram,
            mock_security_groups,
            mock_snapshots,
            mock_volumes,
        ),
    )

    assert status
