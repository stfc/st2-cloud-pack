import json
import requests
from requests.auth import HTTPBasicAuth

from structs.icinga.icinga_account import IcingaAccount
from structs.icinga.object_query import IcingaQuery


def query_object(icinga_account: IcingaAccount, icinga_qurey: IcingaQuery) -> int:
    """
    Schedules a downtime for a host or service
    :param icinga_account: Account for interacting with icinga
    :param icinga_query: Dataclass containing details used to filter and return properties for icinga objects
    :return: Status code
    """
    basic = HTTPBasicAuth(icinga_account.username, icinga_account.password)

    payload = {
        "type": icinga_qurey.object_type.capitalize(),
        "filter": icinga_qurey.filter,
        "filter_vars": icinga_qurey.filter_vars,
        "attrs": icinga_qurey.properties_to_select,
        "joins": icinga_qurey.joins,
    }

    res = requests.post(
        url=f"{icinga_account.icinga_endpoint}/v1/objects/{icinga_qurey.object_type.lower()}s",
        auth=basic,
        verify="/var/lib/icinga2/certs/ca.crt",
        headers={"Accept": "application/json", "X-HTTP-Method-Override": "GET"},
        data=json.dumps(payload),
        timeout=300,
    )

    res.raise_for_status()  # Raises HTTPError, if one occurred

    return res.status_code, res.content
