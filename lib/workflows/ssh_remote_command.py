from ssh_api.exec_command import SSHConnection
from structs.ssh.ssh_connection_details import SSHDetails


def ssh_remote_command(
    host: str, username: str, private_key_path: str, command: str
) -> str:
    """
    Run command on host over SSH
    :param host: Host to run command on
    :param username: Username to authenticate with
    :param private_key_path: Path to private key to authenticate with
    :param command: Command to run on host
    :return: Command output
    """
    connection_details = SSHDetails(
        host=host, username=username, private_key_path=private_key_path
    )
    ssh_client = SSHConnection(connection_details)
    res = ssh_client.run_command_on_host(command)

    return res.decode()
