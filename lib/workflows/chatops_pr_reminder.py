import requests


def pr_reminder(endpoint: str, token: str, channel: str, reminder_type: str) -> None:
    """
    Trigger a pull request reminder message to the Slack workspace
    :param endpoint: Endpoint URL of the ChatOps host
    :param token: Authentication token
    :param channel: Channel to send reminders to
    :param reminder_type: Type of reminder, global or personal
    """
    request = requests.post(
        url=endpoint,
        json={"reminder_type": reminder_type, "channel": channel},
        headers={"Authorization": f"token {token}"}
    )
    request.raise_for_status()