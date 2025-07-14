from dataclasses import dataclass


@dataclass
class SSHDetails:
    """
    Dataclass to hold details for a SSH Connection
    """

    host: str
    username: str
    private_key_path: str
