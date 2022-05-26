from openstack_api.openstack_connection import OpenstackConnection
import requests


def get_amphorae(cloud_account: str):
    """
    Method to get list of amphorae in openstack project
    """
    with OpenstackConnection(cloud_name=cloud_account) as conn:
        if cloud_account == "dev":
            amphorae = requests.get(
                "https://dev-openstack.nubes.rl.ac.uk:9876/v2/octavia/amphorae",
                headers={"X-Auth-Token": conn.auth_token},
            )
        else:
            amphorae = requests.get(
                "https://openstack.nubes.rl.ac.uk:9876/v2/octavia/amphorae",
                headers={"X-Auth-Token": conn.auth_token},
            )
    return amphorae
