from asyncore import poll
import json
from datetime import datetime
from st2reactor.sensor.base import PollingSensor
from st2reactor.container.sensor_wrapper import SensorService
from openstack_api.openstack_connection import OpenstackConnection


class DeletingMachinesSensor(PollingSensor):
    def __init__(self, sensor_service: SensorService, config, poll_interval):
        super(DeletingMachinesSensor, self).__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self.sensor_service: SensorService = sensor_service
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)

    # pylint: disable=useless-super-delegation
    def add_trigger(self, trigger):
        return super().add_trigger(trigger)

    def update_trigger(self, trigger):
        return super().update_trigger(trigger)

    def cleanup(self):
        return super().cleanup()

    def remove_trigger(self, trigger):
        return super().remove_trigger(trigger)

    def setup(self):
        return super().setup()

    def poll(self, cloud_account: str = "dev"):
        """
        Action to check for machines that are stuck deleting for more than 10mins
        Outputs a suitable dictionary to pass into create_tickets
        """
        output = {
            "title": "Server {p[id]} has not been updated in more than 10 minutes during {p[action]}",
            "body": "The following information may be useful\nHost id: {p[id]} \n{p[data]}",
            "server_list": [],
        }

        self.sensor_service.dispatch_with_context(
            payload=output, trigger="openstack.deletingmachines"
        )

        with OpenstackConnection(cloud_name=cloud_account) as conn:
            projects = conn.list_projects()
        for project in projects:
            deleted = self._check_deleted(project=project["id"], cloud=cloud_account)
        output["server_list"].extend(deleted)

        if len(output["server_list"]) > 0:
            self.sensor_service.dispatch_with_context(
                payload=output, trigger="openstack.deletingmachines"
            )
            return output

    @staticmethod
    def _check_deleted(cloud: str, project: str):
        """
        Runs the check for deleting machines on a per-project basis
        """
        output = []

        print("Checking project", project)
        with OpenstackConnection(cloud_name=cloud) as conn:
            server_list = conn.list_servers(
                filters={"all_tenants": True, "project_id": project}
            )
        # Loop through each server in the project/list
        for i in server_list:
            # Take current time and check difference between updated time
            since_update = datetime.utcnow() - datetime.strptime(
                i["updated"], "%Y-%m-%dT%H:%M:%Sz"
            )
            # Check if server has been stuck in deleting for too long.
            # (uses the last updated time so if changes have been made
            # to the server while deleting the check may not work.)
            if i["status"] == "active" and since_update.total_seconds() >= 600:
                # Append data to output array
                output.append(
                    {
                        "dataTitle": {"id": str(i.id), "action": str(i["status"])},
                        "dataBody": {"id": i["id"], "data": json.dumps(i)},
                    }
                )

        return output
