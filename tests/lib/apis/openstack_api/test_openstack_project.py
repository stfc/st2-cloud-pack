from unittest.mock import MagicMock, NonCallableMock
import pytest

from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack.exceptions import ConflictException
from apis.openstack_api.openstack_project import create_project, delete_project


def test_create_project_name_missing_throws():
    """
    Tests calling the API wrapper without a project name will throw
    """
    mock_project_details = MagicMock()
    mock_project_details.name = ""
    mock_project_details.email = "test@test.com"

    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_project(mock_conn, mock_project_details)


def test_create_project_email_missing_throws():
    """
    Tests calling the API wrapper without an email will throw
    """
    mock_project_details = MagicMock()
    mock_project_details.name = "foo"
    mock_project_details.email = ""

    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_project(mock_conn, mock_project_details)


def test_create_project_invalid_email_throws():
    """
    Tests calling the API wrapper with an invalid email will throw
    """
    mock_project_details = MagicMock()
    mock_project_details.name = "foo"
    mock_project_details.email = "invalid-email"

    mock_conn = MagicMock()
    with pytest.raises(ValueError):
        create_project(mock_conn, mock_project_details)


def test_create_project_forwards_error():
    """
    Tests that create_project re-throws ConflictException error
    """
    mock_project_details = MagicMock()
    mock_project_details.name = "foo"
    mock_project_details.email = "test@test.com"

    mock_conn = MagicMock()
    mock_conn.identity.create_project.side_effect = ConflictException()

    with pytest.raises(ConflictException):
        create_project(mock_conn, mock_project_details)


def test_create_project_successful():
    """
    Tests that create project works
    """
    mock_project_details = MagicMock()
    mock_project_details.name = "foo"
    mock_project_details.description = "bar"
    mock_project_details.is_enabled = True
    mock_project_details.email = "test@test.com"
    mock_project_details.parent_id = None
    mock_project_details.immutable = False

    mock_conn = MagicMock()

    res = create_project(mock_conn, mock_project_details)

    mock_conn.identity.create_project.assert_called_once_with(
        name="foo",
        description="bar",
        is_enabled=True,
        tags=["test@test.com"],
    )
    assert res == mock_conn.identity.create_project.return_value


def test_create_project_successful_no_parent_id_and_not_immutable():
    """
    Tests that create project works
    """
    mock_project_details = MagicMock()
    mock_project_details.name = "foo"
    mock_project_details.description = "bar"
    mock_project_details.is_enabled = True
    mock_project_details.email = "test@test.com"
    mock_project_details.parent_id = None
    mock_project_details.immutable = False

    mock_conn = MagicMock()

    res = create_project(mock_conn, mock_project_details)

    mock_conn.identity.create_project.assert_called_once_with(
        name="foo",
        description="bar",
        is_enabled=True,
        tags=["test@test.com"],
    )
    assert res == mock_conn.identity.create_project.return_value


def test_create_project_successful_with_parent_id_and_immutable():
    """
    Tests that the params and result are forwarded as-is to/from the
    create_project API
    """
    mock_project_details = MagicMock()
    mock_project_details.name = "foo"
    mock_project_details.description = "bar"
    mock_project_details.is_enabled = True
    mock_project_details.email = "test@test.com"
    mock_project_details.parent_id = "baz"
    mock_project_details.immutable = True

    mock_conn = MagicMock()

    res = create_project(mock_conn, mock_project_details)

    mock_conn.identity.create_project.assert_called_once_with(
        name="foo",
        description="bar",
        is_enabled=True,
        parent_id="baz",
        tags=["test@test.com", "immutable"],
    )
    assert res == mock_conn.identity.create_project.return_value


def test_delete_immutable_project_throws():
    """
    Tests that trying to deleting an immutable project raises an error
    """
    mock_conn = MagicMock()
    mock_conn.identity.find_project.return_value = {
        "id": "project-id",
        "name": "foo",
        "tags": ["test@test.com", "immutable", "other-tag"],
    }

    mock_project_identifier = NonCallableMock()
    with pytest.raises(ValueError):
        delete_project(mock_conn, mock_project_identifier)

    mock_conn.identity.find_project.assert_called_once_with(
        mock_project_identifier, ignore_missing=False
    )


def test_delete_project_successful_with_name_or_id():
    """
    Tests delete project will use name or Openstack ID if provided
    and will return the result
    """
    mock_conn = MagicMock()
    mock_conn.identity.find_project.return_value = {
        "id": "project-id",
        "name": "foo",
        "tags": ["test@test.com", "other-tag"],
    }
    # meaning it was successful
    mock_conn.identity.delete_project.return_value = None

    mock_project_identifier = NonCallableMock()
    res = delete_project(mock_conn, mock_project_identifier)

    mock_conn.identity.find_project.assert_called_once_with(
        mock_project_identifier, ignore_missing=False
    )

    mock_conn.identity.delete_project.assert_called_once_with(
        project=mock_conn.identity.find_project.return_value, ignore_missing=False
    )
    assert res


@pytest.mark.parametrize(
    "protected_project_id",
    [
        "0e60669c49d4497aad91d8f729cfdd77",
        "4de86830e89b4a46b590536571b6ccd4",
        "c9aee696c4b54f12a645af2c951327dc",
    ],
)
def test_delete_protected_project_fails(protected_project_id):
    """tests that delete_project fails if project has uuid which is unsafe to delete"""
    mock_conn = MagicMock()
    mock_project_identifier = NonCallableMock()
    mock_conn.identity.find_project.return_value = {"id": protected_project_id}

    with pytest.raises(ValueError):
        delete_project(mock_conn, mock_project_identifier)
    mock_conn.identity.find_project.assert_called_once_with(
        mock_project_identifier, ignore_missing=False
    )
    mock_conn.identity.delete_project.assert_not_called()
