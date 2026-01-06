from unittest.mock import MagicMock, patch
import pytest

from workflows.hv_create_test_server import create_test_server_single_hypervisor
from workflows.hv_create_test_server import _str_to_list


@pytest.mark.parametrize("delete_error_server", [True, False])
@patch("workflows.hv_create_test_server.delete_server")
@patch("workflows.hv_create_test_server.build_server")
@patch("workflows.hv_create_test_server.random")
@patch("workflows.hv_create_test_server.get_available_flavors")
def test_create_single_test_server(
    mock_get_available_flavors,
    mock_random,
    mock_build_server,
    mock_delete_server,
    delete_error_server,
):
    """
    Test build single server on a hypervisor
    """
    mock_conn = MagicMock()

    mock_flavors = ["flavor1", "flavor2", "flavor3"]
    mock_get_available_flavors.return_value = mock_flavors

    mock_random.choice.return_value = "flavor2"

    mock_server = MagicMock()
    mock_build_server.return_value = mock_server

    # call the function being tested and verify
    # all dependencies are called with the right arguments
    create_test_server_single_hypervisor(
        mock_conn, "hvxyz.nubes.rl.ac.uk", False, delete_error_server
    )

    mock_get_available_flavors.assert_called_once_with(
        mock_conn, "hvxyz.nubes.rl.ac.uk"
    )
    mock_build_server.assert_called_once_with(
        mock_conn,
        "stackstorm-test-server",
        "flavor2",
        "ubuntu-jammy-22.04-nogui",
        "Internal",
        "hvxyz.nubes.rl.ac.uk",
        delete_error_server,
    )
    mock_delete_server.assert_called_once_with(mock_conn, mock_server.id)


def test_create_test_server_raises_on_empty_hostname():
    """
    Test an Exception is raised when the hostname value passed to function
    create_test_server_single_hypervisor is empty
    """
    mock_conn = MagicMock()

    with pytest.raises(ValueError):
        create_test_server_single_hypervisor(mock_conn, "", False, True)


def test_create_test_server_single_hypervisor_raises_on_comma_in_hostname():
    """
    Test an Exception is raised when the hostname value passed to function
    create_test_server_single_hypervisor includes a comma
    """
    mock_conn = MagicMock()

    with pytest.raises(ValueError):
        create_test_server_single_hypervisor(mock_conn, "hv1,example.com", False, True)


def test_create_test_server_single_hypervisor_raises_on_colon_in_hostname():
    """
    Test an Exception is raised when the hostname value passed to function
    create_test_server_single_hypervisor includes a colon
    """
    mock_conn = MagicMock()

    with pytest.raises(ValueError):
        create_test_server_single_hypervisor(mock_conn, "hv1:example.com", False, True)


@patch("workflows.hv_create_test_server.delete_server")
@patch("workflows.hv_create_test_server.build_server")
@patch("workflows.hv_create_test_server.get_available_flavors")
def test_create_test_server_all_flavors(
    mock_get_available_flavors, mock_build_server, mock_delete_server
):
    """
    Test build all possible flavors on a hypervisor
    """
    mock_conn = MagicMock()
    mock_flavors = ["flavor1", "flavor2", "flavor3"]
    mock_get_available_flavors.return_value = mock_flavors

    mock_server = MagicMock()
    mock_build_server.return_value = mock_server

    create_test_server_single_hypervisor(mock_conn, "hvxyz.nubes.rl.ac.uk", True, True)

    mock_get_available_flavors.assert_called_once_with(
        mock_conn, "hvxyz.nubes.rl.ac.uk"
    )

    for flavor in mock_flavors:
        mock_build_server.assert_any_call(
            mock_conn,
            "stackstorm-test-server",
            flavor,
            "ubuntu-jammy-22.04-nogui",
            "Internal",
            "hvxyz.nubes.rl.ac.uk",
            True,
        )
        mock_delete_server.assert_any_call(mock_conn, mock_server.id)


def test_single_hypervisor_name():
    """Test that a single hypervisor name returns a list with one element"""
    result = _str_to_list("hypervisor1")
    assert result == ["hypervisor1"]
    assert len(result) == 1


def test_multiple_hypervisors_comma_delimited():
    """Test that comma-delimited hypervisor names return a list of strings"""
    result = _str_to_list("hypervisor1, hypervisor2, hypervisor3")
    assert result == ["hypervisor1", "hypervisor2", "hypervisor3"]
    assert len(result) == 3
    assert all(isinstance(item, str) for item in result)


def test_multiple_hypervisors_colon_delimited():
    """Test that colon-delimited hypervisor names return a list of strings"""
    result = _str_to_list("hypervisor1: hypervisor2: hypervisor3")
    assert result == ["hypervisor1", "hypervisor2", "hypervisor3"]
    assert len(result) == 3
    assert all(isinstance(item, str) for item in result)


def test_comma_delimited_with_empty_fields_and_trailing_comma():
    """Test that empty fields and trailing commas are filtered out"""
    result = _str_to_list("foo, bar, , barz,")
    assert result == ["foo", "bar", "barz"]
    assert len(result) == 3
    assert "" not in result


def test_colon_delimited_with_empty_fields_and_trailing_colon():
    """Test that empty fields and trailing colons are filtered out"""
    result = _str_to_list("foo: bar: : barz:")
    assert result == ["foo", "bar", "barz"]
    assert len(result) == 3
    assert "" not in result


def test_mixed_delimiters_raises_value_error():
    """Test that mixing commas and colons raises a ValueError"""
    with pytest.raises(ValueError):
        _str_to_list("hypervisor1, hypervisor2: hypervisor3")
