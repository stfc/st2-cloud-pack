import paramiko
from paramiko.ssh_exception import SSHException

from structs.ssh.ssh_connection_details import SSHDetails


class SSHConnection:
    """
    Class to create a SSH connection and execute remote commands
    """

    def __init__(self, conn: SSHDetails):
        self.host = conn.host
        self.username = conn.username
        self.private_key = paramiko.RSAKey.from_private_key_file(conn.private_key_path)
        self.client = paramiko.SSHClient()

    def __enter__(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.client.connect(self.host, username=self.username, pkey=self.private_key)

        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def run_command_on_host(self, command: str):
        with self as client:
            _stdin, stdout, stderr = client.exec_command(command=command)

            err = stderr.read().decode()
            if err:
                raise SSHException(err)

            return stdout.read()
