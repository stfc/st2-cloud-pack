from unittest.mock import patch, MagicMock

import pytest
from paramiko.ssh_exception import SSHException

from ssh_api.exec_command import SSHConnection


@patch("ssh_api.exec_command.paramiko.SSHClient")
@patch("ssh_api.exec_command.paramiko.RSAKey")
def test_ssh_connection(mock_rsakey, mock_sshclient):
    """
    Tests a client to connect to a atlassian server is created and closed
    """
    mock_details = MagicMock()
    mock_details.host = "example.com"
    mock_details.username = "foo"
    mock_details.private_key_path = "/home/bar"

    with SSHConnection(mock_details) as client:
        mock_sshclient.assert_called_once()
        mock_rsakey.from_private_key_file.assert_called_once_with(
            mock_details.private_key_path
        )
        mock_sshclient.return_value.set_missing_host_key_policy.assert_called_once()
        mock_sshclient.return_value.connect.assert_called_once_with(
            mock_details.host,
            username=mock_details.username,
            pkey=mock_rsakey.from_private_key_file.return_value,
        )

        assert client == mock_sshclient.return_value


@patch("ssh_api.exec_command.paramiko.SSHClient")
@patch("ssh_api.exec_command.paramiko.RSAKey")
def test_run_command_on_host(mock_rsa_key, mock_ssh_client):
    """
    Test execution of command on remote host
    """
    mock_details = MagicMock()
    mock_details.host = "example.com"
    mock_details.username = "foo"
    mock_details.private_key_path = "/home/bar"

    mock_rsa_key.return_value = "mock_key"

    mock_client_instance = MagicMock()
    mock_ssh_client.return_value = mock_client_instance
    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b"test_output"
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""

    mock_client_instance.exec_command.return_value = (None, mock_stdout, mock_stderr)

    ssh_conn = SSHConnection(mock_details)

    output = ssh_conn.run_command_on_host("ls")

    mock_client_instance.exec_command.assert_called_once_with(command="ls")
    assert output == b"test_output"


@patch("ssh_api.exec_command.paramiko.SSHClient")
@patch("ssh_api.exec_command.paramiko.RSAKey")
def test_run_command_on_host_failure(mock_rsa_key, mock_ssh_client):
    """
    Test execution of command on remote host
    """
    mock_details = MagicMock()
    mock_details.host = "example.com"
    mock_details.username = "foo"
    mock_details.private_key_path = "/home/bar"

    mock_rsa_key.return_value = "mock_key"

    mock_client_instance = MagicMock()
    mock_ssh_client.return_value = mock_client_instance
    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b""
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b"test_error"

    mock_client_instance.exec_command.return_value = (None, mock_stdout, mock_stderr)

    ssh_conn = SSHConnection(mock_details)

    with pytest.raises(SSHException, match="test_error"):
        ssh_conn.run_command_on_host("ls")

    mock_client_instance.exec_command.assert_called_once_with(command="ls")
