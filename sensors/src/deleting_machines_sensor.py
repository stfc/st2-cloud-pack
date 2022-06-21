from datetime import datetime
from st2reactor.sensor.base import PollingSensor
from st2reactor.container.sensor_wrapper import SensorService
from openstack_api.openstack_connection import OpenstackConnection


class DeletingMachinesSensor(PollingSensor):
    def __init__(self, sensor_service: SensorService, config, poll_interval):
        # pylint: disable=super-with-arguments
        super(DeletingMachinesSensor, self).__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self.sensor_service: SensorService = sensor_service
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)

    # pylint: disable=missing-function-docstring
    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def cleanup(self):
        pass

    def remove_trigger(self, trigger):
        pass

    def setup(self):
        pass

    def poll(self, cloud_account: str = "dev-admin"):
        """
        Action to check for machines that are stuck deleting for more than 10mins
        Outputs a suitable dictionary to pass into create_tickets
        """
        output = {
            "title": "Server {p[id]} has not been updated in more than 10 minutes during {p[action]}",
            "body": "The following information may be useful\nHost id: {p[id]}",
            "server_list": [],
        }

        with OpenstackConnection(cloud_name=cloud_account) as conn:
            projects = conn.list_projects()
        for project in projects:
            deleted = self._check_deleted(project=project["id"], cloud=cloud_account)
            print(output["server_list"])
            output["server_list"].extend(deleted)
        print(output["server_list"])
        if len(output["server_list"]) > 0:
            self.sensor_service.dispatch_with_context(
                payload=output,
                trigger="stackstorm_openstack.openstack.deletingmachines",
            )
            return output

        print("checks complete, no servers found")
        print(output)
        return output

    @staticmethod
    def _check_deleted(cloud: str, project: str):
        """
        Runs the check for deleting machines on a per-project basis
        """
        output = []

        print("Checking project", project)
        with OpenstackConnection(cloud_name=cloud) as conn:
            server_list = conn.compute.servers(all_tenants=True, project_id=project)

            # Loop through each server in the project/list
            for i in server_list:
                server = conn.compute.get_server(i["id"])
                # Take current time and check difference between updated time
                since_update = datetime.utcnow() - datetime.strptime(
                    server.updated_at, "%Y-%m-%dT%H:%M:%Sz"
                )
                # Check if server has been stuck in deleting for too long.
                # (uses the last updated time so if changes have been made
                # to the server while deleting the check may not work.)
                if server.status == "ACTIVE" and since_update.total_seconds() >= 600:
                    # Append data to output array
                    output.append(
                        {
                            "dataTitle": {
                                "id": str(server.id),
                                "action": str(server.status),
                            },
                            "dataBody": {"id": server.id},
                        }
                    )
                    print(output)
        return output
