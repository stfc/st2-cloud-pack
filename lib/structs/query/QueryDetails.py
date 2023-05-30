from dataclasses import dataclass
from typing import Optional, Set
from enums.query.server.server_properties import ServerProperties


@dataclass
class QueryDetails:
    properties_to_select: Optional[Set[ServerProperties]]
    group_by: Optional[ServerProperties]
    sort_by: Optional[ServerProperties]

    # TODO define some meta openstacksdk args that can be passed into _run_query() as **kwargs
