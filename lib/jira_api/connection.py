import jira
from structs.jira.jira_account import JiraAccount


class JiraConnection:
    """
    Wrapper for Jira connection
    """

    def __init__(self, account: JiraAccount):
        self.conn = None
        self.endpoint = account.atlassian_endpoint
        self.token = account.api_token
        self.username = account.username

    def __enter__(self):
        self.conn = jira.client.JIRA(
            server=self.endpoint,
            basic_auth=(
                self.username,
                self.token,
            ),
        )
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
