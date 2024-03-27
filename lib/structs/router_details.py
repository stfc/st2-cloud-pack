from dataclasses import dataclass


@dataclass
class RouterDetails:
    project_identifier: str

    router_name: str
    router_description: str
    external_gateway: str
    is_distributed: bool
