from typing import List, Optional, Union

import openstack

from enums.query.props import ServerProperties
from enums.query.query_presets import QueryPresetsGeneric
from enums.query.props.hypervisor_properties import HypervisorProperties

from openstack_query import HypervisorQuery, ServerQuery


def find_down_hypervisors(
        cloud_account: str
):
    """
    :param cloud_account: string represents cloud account to use
    """

    hypervisor_query_down = HypervisorQuery()
    hypervisor_query_down.where(
        QueryPresetsGeneric.ANY_IN, HypervisorProperties.HYPERVISOR_STATE, values=["down"]
    )
    hypervisor_query_down.run(
        cloud_account,
    )
    hypervisor_query_down.select(
        HypervisorProperties.HYPERVISOR_ID,
        HypervisorProperties.HYPERVISOR_NAME,
        HypervisorProperties.HYPERVISOR_STATE,
        HypervisorProperties.HYPERVISOR_STATUS,
    )

    return hypervisor_query_down


def find_disabled_hypervisors(
        cloud_account: str
):
    """
    :param cloud_account: string represents cloud account to use
    """

    hypervisor_query_disabled = HypervisorQuery()
    hypervisor_query_disabled.where(
        QueryPresetsGeneric.ANY_IN, HypervisorProperties.HYPERVISOR_STATUS, values=["disabled"]
    )
    hypervisor_query_disabled.run(
        cloud_account,
    )
    hypervisor_query_disabled.select(
        HypervisorProperties.HYPERVISOR_ID,
        HypervisorProperties.HYPERVISOR_NAME,
        HypervisorProperties.HYPERVISOR_STATE,
        HypervisorProperties.HYPERVISOR_STATUS,
    )

    return hypervisor_query_disabled


if __name__ == "__main__":
    find_down_hypervisors("dev")
    find_disabled_hypervisors("dev")
    """
    conn = openstack.connect("dev")
    for hv in conn.compute.hypervisors(details=True):
        print(hv)
"""
