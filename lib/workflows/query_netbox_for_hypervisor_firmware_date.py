import logging
import pynetbox
import requests
from apis.netbox_api.query_netbox import get_hypervisors_by_environment_and_status
from apis.netbox_api.structs.netbox_account import NetboxAccount

logger = logging.getLogger(__name__)


def query_netbox_for_hypervisor_firmware_date(
    netbox_account: NetboxAccount, environment: str, status: str
) -> list[dict]:
    """
    Gets set info from hypervisor
    :param netbox_account: NetboxAccount
    :param environment: String of environment cloud to query ("prod", "staging", "all")
    :param status: String of what status to query
    ("active", "offline", "planned", "staged", "failed", "inventory", "decommissioning")
    """

    try:
        hypervisors = get_hypervisors_by_environment_and_status(
            netbox_account, environment, status
        )
    except pynetbox.RequestError:
        logger.exception("NetBox returned an API error")
        raise
    except requests.exceptions.ConnectionError:
        logger.exception("Could not reach NetBox")
        raise
    except Exception:
        logger.exception("Unexpected error while retrieving hypervisors from NetBox")
        raise

    # Getting name, platform and firmware date metadata from each HV. Name to identify,
    # platform to relate to fw date as rocky 8 has priority in updates and patches
    hypervisor_out = [
        {
            "name": hv.name,
            "platform": hv.platform,
            "status": hv.status,
            "fw_date": hv.custom_fields.get("firmware_last_update")
            or hv.created,  # Fall back to created date if firmware_last_update is not set
        }
        for hv in hypervisors
    ]
    logger.info(
        "Extracted name platform and fw_date metadata from hypervisors -> %s",
        hypervisor_out,
    )
    return hypervisor_out
