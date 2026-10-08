import logging
import pynetbox

from apis.netbox_api.structs.netbox_account import NetboxAccount

logger = logging.getLogger(__name__)

PROD_HV_SLUGS = ["openstack-prod-kolla_compute", "openstack-prod-quattor_compute"]
STAGING_HV_SLUGS = [
    "openstack-staging-kolla_compute",
    "openstack-staging-quattor_compute",
]
ALL_HV_SLUGS = PROD_HV_SLUGS + STAGING_HV_SLUGS


def _get_hypervisors_by_status_and_platform(
    netbox_account: NetboxAccount, environment: str, status: str
) -> list:
    """
    Private function that gets hypervisors by status and platform from Netbox
    :param netbox_account: NetboxAccount
    :param environment: String of what environment to query ("prod", "staging", "all")
    :param status: String of what status to query
    ("active", "offline", "planned", "staged", "failed", "inventory", "decommissioning")
    """

    if environment == "prod":
        slugs = PROD_HV_SLUGS
    elif environment == "staging":
        slugs = STAGING_HV_SLUGS
    elif environment == "all":
        slugs = ALL_HV_SLUGS
    else:
        raise ValueError(f"Unsupported environment: {environment!r}")

    nb = pynetbox.api(netbox_account.netbox_endpoint, token=netbox_account.api_token)
    logger.info("connected to Netbox")

    hypervisors = list(nb.dcim.devices.filter(role=slugs, status=status))
    logger.info("Found %d hypervisors", len(hypervisors))
    return hypervisors


def query_netbox_for_hypervisor_info(
    netbox_account: NetboxAccount, environment: str, status: str
) -> list[dict]:
    """
    Gets set info from hypervisor
    :param netbox_account: NetboxAccount
    :param environment: String of environment cloud to query ("prod", "staging", "all")
    :param status: String of what status to query
    ("active", "offline", "planned", "staged", "failed", "inventory", "decommissioning")
    """
    hypervisors = _get_hypervisors_by_status_and_platform(
        netbox_account, environment, status
    )

    hypervisor_out = [
        {
            "name": hv.name,
            "platform": hv.platform,
            "fw_date": hv.custom_fields.get("firmware_last_update"),
        }
        for hv in hypervisors
    ]
    logger.info("Extracted name platform and fw_date metadata from hypervisors")
    return hypervisor_out
