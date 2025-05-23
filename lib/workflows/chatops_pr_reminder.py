from typing import Dict
import requests


def pr_reminder(endpoint: str, token: str, channel: str, reminder_type: str) -> Dict:
    """
    Send a HTTP post request to the ChatOps app endpoint to trigger a reminder.
    :param endpoint: URL of ChatOps application endpoint
    :param token: Token to authenticate request with
    :param channel: Channel to send the message to
    :param reminder_type: Type of reminder. E.g. global or personal
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {token}"
    }
    body = {
        "reminder_type": reminder_type,
        "channel": channel
    }
    response = requests.post(endpoint, json=body, headers=headers)
    response.raise_for_status()
    return {
        "status_code": response.status_code,
        "response": response.text
    }