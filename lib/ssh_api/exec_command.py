import select
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

    def run_command_on_host(self, command: str):
        """
        Run command on a host
        :param command: Command to run over SSH
        :return: Output bytes
        """
        with self as client:
            stdin, stdout, stderr = client.exec_command(command=command)

            channel = stdout.channel
            stdin.close()
            channel.shutdown_write()
            while (
                not channel.closed
                or channel.recv_ready()
                or channel.recv_stderr_ready()
            ):
                if channel.recv_ready():
                    output = channel.recv(1024).decode("utf-8")
                    print(output, end="")
                if channel.recv_stderr_ready():
                    output = channel.recv_stderr(1024).decode("utf-8")
                    print(output, end="")

                if (
                    stdout.channel.exit_status_ready()
                    and not stderr.channel.recv_stderr_ready()
                    and not stdout.channel.recv_ready()
                ):
                    stdout.channel.shutdown_read()
                    stdout.channel.close()
                    break

            stdout.close()
            stderr.close()

            if stdout.channel.recv_exit_status() != 0:
                raise SSHException()

            return
