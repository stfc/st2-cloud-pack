import pynetbox

from apis.netbox_api.structs.netbox_account import NetboxAccount


def _get_hypervisors_by_status_and_platform(
    netbox_account: NetboxAccount, cloud: str, status: str
) -> list:
    ids = {"prod": [75, 224], "staging": [213, 225], "all": [75, 224, 213, 225]}
    if cloud.casefold() not in ids:
        raise ValueError("Invalid cloud name")
    values = ids[cloud]

    nb = pynetbox.api(netbox_account.netbox_endpoint, token=netbox_account.api_token)

    hypervisors = []
    for value in values:
        hypervisors.extend(list(nb.dcim.devices.filter(role_id=value, status=status)))
    return hypervisors


def get_metadata_from_hypervisor(
    netbox_account: NetboxAccount, cloud: str, status: str
) -> list[dict]:
    hypervisor_list = _get_hypervisors_by_status_and_platform(
        netbox_account, cloud, status
    )

    hypervisor_out = []

    for hypervisor in hypervisor_list:
        hypervisor_out.append(
            {
                "name": hypervisor.name,
                "platform": hypervisor.platform,
                "fw_date": hypervisor.custom_fields["firmware_last_update"],
            }
        )

    return hypervisor_out
