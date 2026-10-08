import pynetbox

from apis.netbox_api.structs.netbox_account import NetboxAccount


def get_devices_by_role(cloud: str, status: str, netbox_account: NetboxAccount) -> list:
    ids = {"prod": [75, 224], "staging": [213, 225], "all": [75, 224, 213, 225]}
    if cloud.casefold() not in ids.keys():
        raise ValueError("Invalid cloud name")
    else:
        values = ids[cloud]

    nb = pynetbox.api(
        netbox_account.netbox_endpoint, token=netbox_account.api_token
    )

    devices = []
    for value in values:
        devices.extend(list(nb.dcim.devices.filter(role_id=value, status="active")))

    return devices
