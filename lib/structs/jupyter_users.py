from dataclasses import dataclass
from typing import Optional


@dataclass
class JupyterUsers:
    name: str
    start_index: Optional[int]
    end_index: Optional[int]
