from unittest.mock import MagicMock, patch

from workflows.hv_create_test_server import create_test_server


@patch("workflows.hv_create_test_server.delete_server")
@patch("workflows.hv_create_test_server.build_server")
@patch("workflows.hv_create_test_server.random")
@patch("workflows.hv_create_test_server.get_available_flavors")
def test_create_single_test_server(
    mock_get_available_flavors, mock_random, mock_build_server, mock_delete_server
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

    create_test_server(mock_conn, "hvxyz.nubes.rl.ac.uk", False)

    mock_get_available_flavors.assert_called_once_with(
        mock_conn, "hvxyz.nubes.rl.ac.uk"
    )
    mock_build_server.assert_called_once_with(
        mock_conn,
        "stackstorm-test-server",
        "flavor2",
        "ubuntu-focal-20.04-nogui",
        "Internal",
        "hvxyz.nubes.rl.ac.uk",
    )
    mock_delete_server.assert_called_once_with(mock_conn, mock_server.id)


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

    create_test_server(mock_conn, "hvxyz.nubes.rl.ac.uk", True)

    mock_get_available_flavors.assert_called_once_with(
        mock_conn, "hvxyz.nubes.rl.ac.uk"
    )

    for flavor in mock_flavors:
        mock_build_server.assert_any_call(
            mock_conn,
            "stackstorm-test-server",
            flavor,
            "ubuntu-focal-20.04-nogui",
            "Internal",
            "hvxyz.nubes.rl.ac.uk",
        )
        mock_delete_server.assert_any_call(mock_conn, mock_server.id)
