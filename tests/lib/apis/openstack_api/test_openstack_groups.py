from unittest.mock import MagicMock
import pytest

from apis.openstack_api.openstack_groups import create_group


@pytest.mark.parametrize(
    "group_name",
    [
        "invalid/group",
        "Invalid-Group",
        "invalid_group",
        "invalid group",
        "invalid@group",
        "",
    ],
)
def test_create_group_raises_value_error_on_invalid_chars(group_name):
    """Test that a ValueError is raised for various invalid group name patterns."""
    conn = MagicMock()
    with pytest.raises(ValueError, match="invalid characters"):
        create_group(conn, group_name)


@pytest.mark.parametrize(
    "group_name",
    [
        "valid-group",
        "group123",
        "123-456",
        "a",
    ],
)
def test_create_group_succeeds_on_valid_names(group_name):
    """Test that valid group names do not raise an error."""
    conn = MagicMock()
    # Assuming create_group returns None or True on success
    create_group(conn, group_name)


def test_create_group_passes_correct_name_without_calling():
    """
    Test that the function attempts to pass the correct group_name
    to the identity service without actually executing the call.
    """
    conn = MagicMock()
    group_name = "test-group"

    # We call the function
    create_group(conn, group_name)

    # Assert that create_group was called with the exact group_name
    conn.identity.create_group.assert_called_once_with(group_name)
