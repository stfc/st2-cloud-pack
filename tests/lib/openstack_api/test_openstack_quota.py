from unittest.mock import MagicMock, call
import pytest

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_quota import set_quota
from structs.quota_details import QuotaDetails


def test_set_quota_project_missing():
    """
    Tests that set quota raises error when project identifier missing
    """
    mock_details = QuotaDetails(
        project_identifier="  ", num_floating_ips=1, num_security_group_rules=1
    )
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        set_quota(mock_conn, mock_details)


def test_set_quota_floating_ips():
    """
    Tests that setting floating IPs update the quota correctly
    """
    mock_details = QuotaDetails(
        project_identifier="foo", num_floating_ips=1, num_security_group_rules=0
    )
    mock_conn = MagicMock()
    set_quota(mock_conn, mock_details)
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.network.update_quota.assert_called_once_with(
        quota=mock_conn.identity.find_project.return_value.id, floating_ips=1
    )


def test_set_quota_security_group_rules():
    """
    Tests that setting security group rules update the quota correctly
    """
    mock_details = QuotaDetails(
        project_identifier="foo", num_floating_ips=0, num_security_group_rules=1
    )
    mock_conn = MagicMock()
    set_quota(mock_conn, mock_details)
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.network.update_quota.assert_called_once_with(
        quota=mock_conn.identity.find_project.return_value.id, security_group_rules=1
    )


def test_set_quota_everything():
    """
    Tests that setting every supported quota in a single test
    """
    mock_details = QuotaDetails(
        project_identifier="foo", num_floating_ips=10, num_security_group_rules=20
    )
    mock_conn = MagicMock()
    set_quota(mock_conn, mock_details)
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.network.update_quota.assert_has_calls(
        [
            call(
                quota=mock_conn.identity.find_project.return_value.id, floating_ips=10
            ),
            call(
                quota=mock_conn.identity.find_project.return_value.id,
                security_group_rules=20,
            ),
        ]
    )
