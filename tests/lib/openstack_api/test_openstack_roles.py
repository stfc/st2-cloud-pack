from unittest.mock import MagicMock
import pytest

from enums.user_domains import UserDomains
from openstack_api.openstack_roles import assign_role_to_user, remove_role_from_user
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from structs.role_details import RoleDetails


@pytest.fixture(name="missing_param_test")
def error_test_fixture():
    """runs a test which expects an error to be raised a specified parameter is empty"""

    def internal_test(mock_fn, mock_conn, mock_details):
        with pytest.raises(MissingMandatoryParamError):
            mock_fn(mock_conn, mock_details)

    return internal_test


def test_assign_roles_throws_missing_project(missing_param_test):
    """
    Tests that an exception is thrown if the specified project is missing
    """
    mock_conn = MagicMock()
    missing_param_test(
        assign_role_to_user,
        mock_conn,
        RoleDetails(
            user_identifier="foo",
            user_domain=UserDomains.STFC,
            project_identifier="  ",
            role_identifier="bar",
        ),
    )
    mock_conn.identity.assign_project_role_to_user.assert_not_called()


def test_assign_roles_throws_missing_user(missing_param_test):
    """
    Tests that an exception is thrown if the specified user is missing
    """
    mock_conn = MagicMock()
    missing_param_test(
        assign_role_to_user,
        mock_conn,
        RoleDetails(
            user_identifier="  ",
            user_domain=UserDomains.STFC,
            project_identifier="foo",
            role_identifier="bar",
        ),
    )
    mock_conn.identity.assign_project_role_to_user.assert_not_called()


def test_assign_roles_throws_missing_role(missing_param_test):
    """
    Tests that an exception is thrown if the specified role is missing
    """
    mock_conn = MagicMock()
    missing_param_test(
        assign_role_to_user,
        mock_conn,
        RoleDetails(
            user_identifier="foo",
            user_domain=UserDomains.STFC,
            project_identifier="bar",
            role_identifier="  ",
        ),
    )
    mock_conn.identity.assign_project_role_to_user.assert_not_called()


def test_assign_roles_successful():
    """
    Tests that assignment is successful
    """
    mock_role_details = RoleDetails(
        user_identifier="foo",
        user_domain=UserDomains.STFC,
        project_identifier="bar",
        role_identifier="baz",
    )
    mock_conn = MagicMock()
    assign_role_to_user(mock_conn, mock_role_details)

    mock_conn.identity.find_project.assert_called_once_with("bar", ignore_missing=False)
    mock_conn.identity.find_domain.assert_called_once_with("stfc", ignore_missing=False)
    mock_conn.identity.find_user.assert_called_once_with(
        "foo",
        domain_id=mock_conn.identity.find_domain.return_value.id,
        ignore_missing=False,
    )
    mock_conn.identity.find_role.assert_called_once_with("baz", ignore_missing=False)

    mock_conn.identity.assign_project_role_to_user.assert_called_once_with(
        project=mock_conn.identity.find_project.return_value,
        user=mock_conn.identity.find_user.return_value,
        role=mock_conn.identity.find_role.return_value,
    )


def test_remove_roles_throws_missing_project(missing_param_test):
    """
    Tests that an exception is thrown if the specified project is missing
    """
    mock_conn = MagicMock()
    missing_param_test(
        remove_role_from_user,
        mock_conn,
        RoleDetails(
            user_identifier="foo",
            user_domain=UserDomains.STFC,
            project_identifier="   ",
            role_identifier="bar",
        ),
    )
    mock_conn.identity.unassign_project_role_from_user.assert_not_called()


def test_remove_roles_throws_missing_user(missing_param_test):
    """
    Tests that an exception is thrown if the specified user is missing
    """
    mock_conn = MagicMock()
    missing_param_test(
        remove_role_from_user,
        mock_conn,
        RoleDetails(
            user_identifier="  ",
            user_domain=UserDomains.STFC,
            project_identifier="foo",
            role_identifier="bar",
        ),
    )
    mock_conn.identity.unassign_project_role_from_user.assert_not_called()


def test_remove_roles_throws_missing_role(missing_param_test):
    """
    Tests that an exception is thrown if the specified role is missing
    """
    mock_conn = MagicMock()
    missing_param_test(
        remove_role_from_user,
        mock_conn,
        RoleDetails(
            user_identifier="foo",
            user_domain=UserDomains.STFC,
            project_identifier="bar",
            role_identifier="  ",
        ),
    )
    mock_conn.identity.unassign_project_role_from_user.assert_not_called()


def test_remove_roles_successful():
    """
    Tests that remove role is successful
    """
    mock_role_details = RoleDetails(
        user_identifier="foo",
        user_domain=UserDomains.STFC,
        project_identifier="bar",
        role_identifier="baz",
    )
    mock_conn = MagicMock()
    remove_role_from_user(mock_conn, mock_role_details)

    mock_conn.identity.find_project.assert_called_once_with("bar", ignore_missing=False)
    mock_conn.identity.find_domain.assert_called_once_with("stfc", ignore_missing=False)
    mock_conn.identity.find_user.assert_called_once_with(
        "foo",
        domain_id=mock_conn.identity.find_domain.return_value.id,
        ignore_missing=False,
    )
    mock_conn.identity.find_role.assert_called_once_with("baz", ignore_missing=False)

    mock_conn.identity.unassign_project_role_from_user.assert_called_once_with(
        project=mock_conn.identity.find_project.return_value,
        user=mock_conn.identity.find_user.return_value,
        role=mock_conn.identity.find_role.return_value,
    )
