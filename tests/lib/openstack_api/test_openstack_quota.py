import dataclasses
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
        project_identifier="  ", floating_ips=1, security_group_rules=1, cores=1, gigabytes=1, instances=1,
        backups=1, ram=1, security_groups=1, snapshots=1, volumes=1
    )
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        set_quota(mock_conn, mock_details)


def test_set_quota_floating_ips():
    """
    Tests that setting floating IPs update the quota correctly
    """
    mock_details = QuotaDetails(
        project_identifier="foo", floating_ips=1, security_group_rules=0, cores=0, gigabytes=0, instances=0,
        backups=0, ram=0, security_groups=0, snapshots=0, volumes=0
    )
    mock_conn = MagicMock()
    set_quota(mock_conn, mock_details)
    kwargs = dataclasses.asdict(mock_details)
    kwargs.pop("project_identifier")
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.set_compute_quotas.assert_called_once_with(
        mock_conn.identity.find_project.return_value.id, **kwargs
    )


def test_set_quota_security_group_rules():
    """
    Tests that setting security group rules update the quota correctly
    """
    mock_details = QuotaDetails(
        project_identifier="foo", floating_ips=0, security_group_rules=1, cores=0, gigabytes=0, instances=0,
        backups=0, ram=0, security_groups=0, snapshots=0, volumes=0
    )
    mock_conn = MagicMock()
    set_quota(mock_conn, mock_details)
    kwargs = dataclasses.asdict(mock_details)
    kwargs.pop("project_identifier")
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.set_compute_quotas.assert_called_once_with(
        mock_conn.identity.find_project.return_value.id, **kwargs
    )


def test_set_quota_everything():
    """
    Tests that setting every supported quota in a single test
    """
    mock_details = QuotaDetails(
        project_identifier="foo", floating_ips=10, security_group_rules=20, cores=8, gigabytes=10, instances=10,
        backups=4, ram=64, security_groups=10, snapshots=4, volumes=10
    )
    mock_conn = MagicMock()
    set_quota(mock_conn, mock_details)
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    kwargs = dataclasses.asdict(mock_details)
    kwargs.pop("project_identifier")
    mock_conn.identity.find_project.assert_called_once_with("foo", ignore_missing=False)
    mock_conn.set_compute_quotas.assert_called_once_with(
        mock_conn.identity.find_project.return_value.id, **kwargs
    )
