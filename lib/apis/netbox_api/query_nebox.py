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


def get_hypervisors_by_environment_and_status(
    netbox_account: NetboxAccount,
    environment: str,
    status: str,
) -> list:
    """
    gets hypervisors by status and platform from Netbox
    :param netbox_account: NetboxAccount
    :param environment: String of what environment to query ("prod", "staging", "all")
    :param status: String of what status to query
    ("active", "offline", "planned", "staged", "failed", "inventory", "decommissioning"
    or "any")
    """

    if environment.strip().casefold() == "prod":
        slugs = PROD_HV_SLUGS
    elif environment.strip().casefold() == "staging":
        slugs = STAGING_HV_SLUGS
    elif environment.strip().casefold() == "all":
        slugs = ALL_HV_SLUGS
    else:
        raise ValueError(f"Unsupported environment: {environment!r}")

    filters: dict[str, str | list[str]] = {"role": slugs}
    if status.strip().casefold() != "any":
        filters["status"] = status

    print("before")
    nb = pynetbox.api(netbox_account.netbox_endpoint, token=netbox_account.api_token)
    logger.info("connected to Netbox")

    hypervisors = list(nb.dcim.devices.filter(**filters))

    logger.info("Found %d hypervisors", len(hypervisors))
    return hypervisors
