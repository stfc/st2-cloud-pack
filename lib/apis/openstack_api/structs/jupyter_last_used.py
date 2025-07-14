from datetime import datetime
from typing import Tuple

# Dataclass will not serialise through rules layer
JupyterLastUsed = Tuple[str, datetime]
