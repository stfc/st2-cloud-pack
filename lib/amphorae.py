from openstack_api.openstack_connection import OpenstackConnection
import requests


DEV_URL = "https://dev-openstack.nubes.rl.ac.uk:9876/v2/octavia/amphorae"
PROD_URL = "https://openstack.nubes.rl.ac.uk:9876/v2/octavia/amphorae"


def get_amphorae(cloud_account: str):
    """
    Method to get list of amphorae in openstack project
    """

    url = DEV_URL if "dev".casefold() in cloud_account.casefold() else PROD_URL
    with OpenstackConnection(cloud_name=cloud_account) as conn:
        return requests.get(
            url,
            headers={"X-Auth-Token": conn.auth_token},
        )
