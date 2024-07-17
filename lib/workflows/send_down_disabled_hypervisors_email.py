from typing import List, Optional, Union

from enums.query.props import ServerProperties
from enums.query.query_presets import QueryPresetsGeneric
from enums.query.props.hypervisor_properties import HypervisorProperties

from openstack_query import HypervisorQuery, ServerQuery


def find_down_hypervisors(
        cloud_account: str, from_projects: Optional[List[str]] = None
):
    """
    :param cloud_account: string represents cloud account to use
    :param from_projects: A list of project identifiers to limit search in
    """

    hypervisor_query = HypervisorQuery()
    hypervisor_query.where(
        QueryPresetsGeneric.ANY_IN, HypervisorProperties.HYPERVISOR_STATE, values="DOWN"
    )
    hypervisor_query.run(
        cloud_account,
        from_projects=from_projects if from_projects else None,
    )

    print(hypervisor_query.to_string())


if __name__ == "__main__":
    find_down_hypervisors("prod")
