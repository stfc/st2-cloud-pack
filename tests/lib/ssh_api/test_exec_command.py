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
    mock_stderr = MagicMock()
    mock_stdin = MagicMock()

    mock_stdout.channel.recv_exit_status.return_value = 0
    mock_stdout.channel.recv_ready.side_effect = [True, True, True, False, False]
    mock_stdout.channel.exit_status_ready.side_effect = [False, True]
    mock_stdout.channel.recv.return_value = b"output"

    mock_client_instance.exec_command.return_value = (
        mock_stdin,
        mock_stdout,
        mock_stderr,
    )

    instance = SSHConnection(mock_details)
    instance.run_command_on_host("ls")

    mock_client_instance.exec_command.assert_called_once_with(command="ls")

    mock_stdout.channel.shutdown_read.assert_called_once()

    mock_stdout.close.assert_called_once()
    mock_stderr.close.assert_called_once()


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
    mock_stderr = MagicMock()
    mock_stdin = MagicMock()

    mock_stdout.channel.recv_exit_status.return_value = 1
    mock_stdout.channel.recv_ready.side_effect = [True, False, False]
    mock_stdout.channel.exit_status_ready.side_effect = [False, False, False, True]
    mock_stdout.channel.recv.return_value = b"output"

    mock_client_instance.exec_command.return_value = (
        mock_stdin,
        mock_stdout,
        mock_stderr,
    )

    instance = SSHConnection(mock_details)

    with pytest.raises(SSHException):
        instance.run_command_on_host("ls")
