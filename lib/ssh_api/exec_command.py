import paramiko
from paramiko.ssh_exception import SSHException

from structs.ssh.ssh_connection_details import SSHDetails


class SSHConnection:
    """
    Class to create a SSH connection and execute remote commands
    """

    def __init__(self, conn: SSHDetails):
        """
        Create SSH client and load private key
        """
        self.host = conn.host
        self.username = conn.username
        self.private_key = paramiko.RSAKey.from_private_key_file(conn.private_key_path)
        self.client = paramiko.SSHClient()

    def __enter__(self):
        """
        Connect host via SSH
        """
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.client.connect(self.host, username=self.username, pkey=self.private_key)

        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close ssh client
        """
        self.client.close()

    def run_command_on_host(self, command: str) -> bytes:
        """
        Run command on a host
        :param command: Command to run over SSH
        :return: Output bytes
        """
        with self as client:
            _stdin, stdout, stderr = client.exec_command(command=command)

            err = stderr.read().decode()
            if err:
                raise SSHException(err)

            return stdout.read()
