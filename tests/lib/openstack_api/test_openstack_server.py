from datetime import datetime
import unittest
from unittest.mock import MagicMock
from openstack_api.openstack_server import migrate_server, snapshot_server


class TestLiveMigration(unittest.TestCase):
    """
    Test Live migrations
    """

    def test_live_migrate_server_without_dest_host(self):
        """
        Test live migration of server, without defined destination host
        """
        mock_connection = MagicMock()
        mock_server_id = "server1"
        migrate_server(conn=mock_connection, server_id=mock_server_id, live=True)

        mock_connection.compute.live_migrate_server.assert_called_once_with(
            server=mock_server_id, host=None, block_migration=True
        )
        mock_connection.compute.migrate_server.assert_not_called()

    def test_live_migrate_server_with_dest_host(self):
        """
        Test live migration of server, without defined destination host
        """
        mock_connection = MagicMock()
        mock_server_id = "server1"
        mock_dest_host = "hv01"
        migrate_server(
            conn=mock_connection,
            server_id=mock_server_id,
            dest_host=mock_dest_host,
            live=True,
        )

        mock_connection.compute.live_migrate_server.assert_called_once_with(
            server=mock_server_id, host=mock_dest_host, block_migration=True
        )
        mock_connection.compute.migrate_server.assert_not_called()


class TestColdMigration(unittest.TestCase):
    """
    Test cold migrations
    """

    def test_migrate_server_without_dest_host(self):
        """
        Test migration of server, without defined destination host
        """
        mock_connection = MagicMock()
        mock_server_id = "server1"
        migrate_server(conn=mock_connection, server_id=mock_server_id, live=False)

        mock_connection.compute.migrate_server.assert_called_once_with(
            server=mock_server_id, host=None
        )
        mock_connection.compute.live_migrate_server.assert_not_called()

    def test_migrate_server_with_dest_host(self):
        """
        Test live migration of server, without defined destination host
        """
        mock_connection = MagicMock()
        mock_server_id = "server1"
        mock_dest_host = "hv01"
        migrate_server(
            conn=mock_connection,
            server_id=mock_server_id,
            dest_host=mock_dest_host,
            live=False,
        )

        mock_connection.compute.migrate_server.assert_called_once_with(
            server=mock_server_id, host=mock_dest_host
        )
        mock_connection.compute.live_migrate_server.assert_not_called()


class TestServerSnapshot(unittest.TestCase):
    """
    Test cases for server snapshots
    """

    def test_snapshot_server(self):
        """
        Test server snapshot
        """
        mock_connection = MagicMock()
        mock_server_id = "server1"
        current_time = datetime.now().strftime("%d-%m-%Y-%H%M")

        mock_project_id = "project1"
        mock_connection.compute.find_server.return_value.project_id = mock_project_id

        mock_image = MagicMock()
        mock_connection.compute.create_server_image.return_value = mock_image

        snapshot_server(conn=mock_connection, server_id=mock_server_id)

        mock_connection.compute.find_server.assert_called_once_with(
            mock_server_id, all_projects=True
        )
        mock_connection.compute.create_server_image.assert_called_once_with(
            server=mock_server_id,
            name=f"{mock_server_id}-{current_time}",
            wait=True,
            timeout=300,
        )
        mock_connection.image.update_image.assert_called_once_with(
            mock_image, owner=mock_project_id
        )
