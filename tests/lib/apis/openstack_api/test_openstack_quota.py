from unittest.mock import MagicMock

import pytest
from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from apis.openstack_api.openstack_quota import set_quota, show_quota
from apis.openstack_api.structs.quota_details import QuotaDetails


def test_set_quota_project_missing():
    """
    Tests that set quota raises error when project identifier missing
    """
    mock_details = QuotaDetails(
        project_identifier="  ",
        floating_ips=1,
        security_group_rules=1,
        cpu_cores=1,
        cinder_storage=1,
        ram=1,
        instances=1,
        backups=1,
        security_groups=1,
        snapshots=1,
        volumes=1,
    )
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        set_quota(mock_conn, mock_details)


def test_set_quota_cores():
    """
    Tests that setting cores update the quota correctly
    """
    mock_details = QuotaDetails(
        project_identifier="foo",
        floating_ips=None,
        security_group_rules=None,
        cpu_cores=1,
        cinder_storage=None,
        ram=None,
        instances=None,
        backups=None,
        security_groups=None,
        snapshots=None,
        volumes=None,
    )
    mock_conn = MagicMock()
    set_quota(mock_conn, mock_details)
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.set_compute_quotas.assert_called_once_with(
        mock_conn.identity.find_project.return_value.id, cpu_cores=1
    )
    mock_conn.set_network_quotas.assert_not_called()
    mock_conn.set_volume_quotas.assert_not_called()


def test_set_quota_security_group_rules():
    """
    Tests that setting security group rules update the quota correctly
    """
    mock_details = QuotaDetails(
        project_identifier="foo",
        floating_ips=None,
        security_group_rules=1,
        cpu_cores=None,
        cinder_storage=None,
        ram=None,
        instances=None,
        backups=None,
        security_groups=None,
        snapshots=None,
        volumes=None,
    )
    mock_conn = MagicMock()
    set_quota(mock_conn, mock_details)
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.set_network_quotas.assert_called_once_with(
        mock_conn.identity.find_project.return_value.id, security_group_rules=1
    )
    mock_conn.set_compute_quotas.assert_not_called()
    mock_conn.set_volume_quotas.assert_not_called()


def test_set_quota_everything():
    """
    Tests that setting every supported quota in a single test
    """
    mock_details = QuotaDetails(
        project_identifier="foo",
        floating_ips=10,
        security_group_rules=20,
        cpu_cores=8,
        cinder_storage=10,
        ram=64,
        instances=10,
        backups=4,
        security_groups=10,
        snapshots=4,
        volumes=10,
    )
    mock_conn = MagicMock()
    set_quota(mock_conn, mock_details)
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.set_compute_quotas.assert_called_once_with(
        mock_conn.identity.find_project.return_value.id,
        cpu_cores=8,
        instances=10,
        ram=64,
    )
    mock_conn.set_network_quotas.assert_called_once_with(
        mock_conn.identity.find_project.return_value.id,
        floating_ips=10,
        security_group_rules=20,
        security_groups=10,
    )
    mock_conn.set_volume_quotas.assert_called_once_with(
        mock_conn.identity.find_project.return_value.id,
        volumes=10,
        snapshots=4,
        cinder_storage=10,
        backups=4,
    )


def test_show_quota_calls_get_compute_quotas():
    """
    Tests that show_quota correctly calls get_compute_quotas with project ID
    """
    mock_conn = MagicMock()
    project_id = "test-project-id"

    show_quota(mock_conn, project_id)

    mock_conn.get_compute_quotas.assert_called_once_with(project_id)
