from dataclasses import dataclass, fields
from typing import Dict


@dataclass
class SMTPAccount:
    username: str
    password: str
    server: str
    port: int
    secure: bool
    smtp_auth: bool

    @staticmethod
    def from_dict(dictionary: Dict):
        """
        Returns instance of this dataclass from a dictionary (for loading from config)
        """
        field_set = {field.name for field in fields(SMTPAccount) if field.init}
        filtered_arg_dict = {
            key: value for key, value in dictionary.items() if key in field_set
        }
        return SMTPAccount(**filtered_arg_dict)
