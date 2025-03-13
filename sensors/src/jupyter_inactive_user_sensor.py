from dateutil.relativedelta import relativedelta

from jupyter_api.api_endpoints import API_ENDPOINTS
from jupyter_api.user_api import UserApi
from st2reactor.sensor.base import PollingSensor

THRESHOLD = relativedelta(days=90)


class JupyterInactiveUserSensor(PollingSensor):
    """
    Polls for accounts that have not logged in for a given amount of time
    """

    def __init__(self, sensor_service, config=None, poll_interval=5):
        """
        Init to prep injected vars
        """
        super().__init__(sensor_service, config, poll_interval)
        self._log = self._sensor_service.get_logger(__name__)
        self._api: UserApi = UserApi()
        self._credentials = {"dev": None, "prod": None, "training": None}

    def poll(self):
        """
        Polls for inactive users and dispatches triggers if any are found
        """
        for endpoint in API_ENDPOINTS.keys():
            inactive_users = self._api.get_inactive_users(
                endpoint, auth_token=self._credentials[endpoint], threshold=THRESHOLD
            )
            if not inactive_users:
                continue

            self._log.info(f"Found {len(inactive_users)} inactive users on {endpoint}")
            self._log.info(f"Inactive users: {inactive_users}")

            inactive_usernames = [user[0] for user in inactive_users]
            self.sensor_service.dispatch(
                trigger="stackstorm_openstack.jupyter.inactiveusers",
                payload={"env": endpoint, "inactive_users": inactive_usernames},
            )

    def setup(self):
        """
        Sets up the sensor
        """
        self._credentials["prod"] = self.sensor_service.get_value(
            "jupyter.prod_token", local=False, decrypt=True
        )
        self._credentials["dev"] = self.sensor_service.get_value(
            "jupyter.dev_token", local=False, decrypt=True
        )
        self._credentials["training"] = self.sensor_service.get_value(
            "jupyter.training_token", local=False, decrypt=True
        )

    def cleanup(self):
        """
        Stub
        """

    def add_trigger(self, trigger):
        """
        Stub
        """

    def update_trigger(self, trigger):
        """
        Stub
        """

    def remove_trigger(self, trigger):
        """
        Stub
        """
