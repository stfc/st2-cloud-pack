from unittest.mock import patch, MagicMock
from structs.quota_details import QuotaDetails
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
    mock_num_floating_ips = 1
    mock_num_security_group_rules = 1

    status = quota_set(
        mock_conn,
        mock_project_identifier,
        mock_num_floating_ips,
        mock_num_security_group_rules,
    )

    mock_api_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            mock_project_identifier,
            mock_num_floating_ips,
            mock_num_security_group_rules,
        ),
    )

    assert status
