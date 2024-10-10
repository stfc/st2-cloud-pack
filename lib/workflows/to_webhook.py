import json
import os
from typing import Dict, List
import requests


def to_webhook(webhook: str, payload: List[Dict]) -> None:
    """
    Send post request to a stackstorm webhook
    :param webhook: Webhook url path
    :param payload: Data to send to webhook
    """
    webhook_url = f'{os.environ["ST2_ACTION_API_URL"]}/webhooks/{webhook}'

    for data in payload:
        res = requests.post(
            url=webhook_url,
            headers={"X-Auth-Token": os.environ["ST2_ACTION_AUTH_TOKEN"]},
            timeout=300,
            data=json.dumps(data),
            verify=False,
        )
        if not res.status_code == 202:
            raise requests.exceptions.HTTPError(res)
