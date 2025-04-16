from st2reactor.sensor.base import PollingSensor

class ChatOpsPRReminderSensor(PollingSensor):
    """Periodically poll the Cloud ChatOps endpoint to trigger the weekly PR reminder."""

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        # At sensor startup, self.config holds the pack’s config
        if not self.config:
            raise ValueError("No config found for sensor")
        self.token = self.config["chatops_token"]
        self.endpoint = self.config["chatops_endpoint"]
        self.channel = self.config["chatops_channel"]
        self.reminder_type = "global"

    def setup(self):
        """Setup method"""

    def poll(self):
        """Poll the ChatOps endpoint."""
        self.sensor_service.dispatch(
            trigger="chatops.pr_reminder", payload={
                "token": self.token,
                "endpoint": self.endpoint,
                "channel": self.channel,
                "reminder_type": self.reminder_type
            }
        )

    def cleanup(self):
        """Clean up method"""

    def add_trigger(self, trigger):
        """This method is called when trigger is created"""

    def update_trigger(self, trigger):
        """This method is called when trigger is updated"""

    def remove_trigger(self, trigger):
        """This method is called when trigger is deleted"""