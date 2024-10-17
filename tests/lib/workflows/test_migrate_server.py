import unittest
from unittest.mock import MagicMock, patch
from workflows.migrate_server import server_migration


class TestServerMigrationWorkflow(unittest.TestCase):
    """
    Test cases for the server migration workflow
    """

    @patch("workflows.migrate_server.migrate_server")
    @patch("workflows.migrate_server.snapshot_server")
    def test_live_server_migration_without_dest_host(
        self, mock_snapshot_server, mock_migrate_server
    ):
        """
        Test live server migration workflow without a destination host
        """
        mock_connection = MagicMock()
        mock_server_id = "server1"

        server_migration(
            conn=mock_connection,
            server_id=mock_server_id,
            destination_host=None,
            live=True,
        )

        mock_snapshot_server.assert_called_once_with(mock_connection, mock_server_id)
        mock_migrate_server.assert_called_once_with(
            mock_connection, server_id=mock_server_id, dest_host=None, live=True
        )

    @patch("workflows.migrate_server.migrate_server")
    @patch("workflows.migrate_server.snapshot_server")
    def test_live_server_migration_with_dest_host(
        self, mock_snapshot_server, mock_migrate_server
    ):
        """
        Test live server migration workflow with a destination host
        """
        mock_connection = MagicMock()
        mock_server_id = "server1"
        mock_dest_host = "hv01"

        server_migration(
            conn=mock_connection,
            server_id=mock_server_id,
            destination_host=mock_dest_host,
            live=True,
        )

        mock_snapshot_server.assert_called_once_with(mock_connection, mock_server_id)
        mock_migrate_server.assert_called_once_with(
            mock_connection,
            server_id=mock_server_id,
            dest_host=mock_dest_host,
            live=True,
        )

    @patch("workflows.migrate_server.migrate_server")
    @patch("workflows.migrate_server.snapshot_server")
    def test_cold_server_migration_without_dest_host(
        self, mock_snapshot_server, mock_migrate_server
    ):
        """
        Test cold server migration workflow without a destination host
        """
        mock_connection = MagicMock()
        mock_server_id = "server1"

        server_migration(
            conn=mock_connection,
            server_id=mock_server_id,
            destination_host=None,
            live=False,
        )

        mock_snapshot_server.assert_called_once_with(mock_connection, mock_server_id)
        mock_migrate_server.assert_called_once_with(
            mock_connection, server_id=mock_server_id, dest_host=None, live=False
        )

    @patch("workflows.migrate_server.migrate_server")
    @patch("workflows.migrate_server.snapshot_server")
    def test_cold_server_migration_with_dest_host(
        self, mock_snapshot_server, mock_migrate_server
    ):
        """
        Test cold server migration workflow with a destination host
        """
        mock_connection = MagicMock()
        mock_server_id = "server1"
        mock_dest_host = "hv01"

        server_migration(
            conn=mock_connection,
            server_id=mock_server_id,
            destination_host=mock_dest_host,
            live=False,
        )

        mock_snapshot_server.assert_called_once_with(mock_connection, mock_server_id)
        mock_migrate_server.assert_called_once_with(
            mock_connection,
            server_id=mock_server_id,
            dest_host=mock_dest_host,
            live=False,
        )
