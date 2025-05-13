import eventlet
from st2reactor.sensor.base import Sensor
import requests
import schedule


class ChatOpsPRReminderSensor(Sensor):
    """Periodically poll the Cloud ChatOps endpoint to trigger the weekly PR reminder."""

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        # At sensor startup, self.config holds the pack’s config
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)
        if not self.config:
            raise ValueError("No config found for sensor")
        self._logger.debug(self.config)
        self.token = self.config["chatops_sensor"]["token"]
        self.endpoint = self.config["chatops_sensor"]["endpoint"]
        self.channel = self.config["chatops_sensor"]["channel"]
        self.reminder_type = "global"
        self._stop = False

    def setup(self):
        """Setup method"""
        schedule.every().monday.at("09:00").do(self.make_request)
        schedule.every().wednesday.at("09:00").do(self.make_request)
        schedule.every().friday.at("09:00").do(self.make_request)

    def make_request(self):
        """Make the request to the ChatOps endpoint."""
        self._logger.debug("ChatOpsPRReminderSensor making request...")
        request = requests.post(
            url=self.endpoint,
            json={"reminder_type": self.reminder_type, "channel": self.channel},
            headers={"Authorization": f"token {self.token}"}
        )
        self._logger.error(f"ChatOpsPRReminderSensor request result with {request.status_code} {request.text}")

    def run(self):
        """Poll the ChatOps endpoint."""
        while not self._stop:
            schedule.run_pending()
            eventlet.sleep(60)

    def cleanup(self):
        """Clean up method"""

    def add_trigger(self, trigger):
        """This method is called when trigger is created"""

    def update_trigger(self, trigger):
        """This method is called when trigger is updated"""

    def remove_trigger(self, trigger):
        """This method is called when trigger is deleted"""