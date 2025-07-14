from unittest.mock import patch

from apis.ssh_api.structs.ssh_connection_details import SSHDetails
from workflows.ssh_remote_command import ssh_remote_command


@patch("workflows.ssh_remote_command.SSHConnection")
def test_remote_command(mock_ssh_conn):
    mock_host = "test_host"
    mock_username = "stackstorm"
    mock_private_key_path = "/home/stackstorm/.ssh/id_rsa"
    mock_command = "ls"

    ssh_remote_command(
        host=mock_host,
        username=mock_username,
        private_key_path=mock_private_key_path,
        command=mock_command,
    )

    mock_ssh_conn.assert_called_once_with(
        SSHDetails(
            host=mock_host,
            username=mock_username,
            private_key_path=mock_private_key_path,
        )
    )
    mock_ssh_conn.return_value.run_command_on_host.assert_called_once_with(mock_command)
