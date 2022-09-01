"""TODO:
hypervisor show
hypervisor reboot
hypervisor schedule downtime
hypervisor remove downtime
hypervisor service enable
hypervisor service disable
"""
import datetime
import json

import requests
from openstack.exceptions import ResourceNotFound

from openstack_action import OpenstackAction


class Hypervisor(OpenstackAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.func = {
            "hypervisor_reboot": self.hypervisor_reboot,
            "hypervisor_schedule_icinga_downtime": self.schedule_icinga_downtime,
            "hypervisor_remove_icinga_downtime": self.remove_icinga_downtime,
            "hypervisor_service_enable": lambda **kwargs: self.hypervisor_service_status(
                func="enable", **kwargs
            ),
            "hypervisor_service_disable": lambda **kwargs: self.hypervisor_service_status(
                func="disable", **kwargs
            ),
            "hypervisor_show": self.hypervisor_show
            # hypervisor create
            # hypervisor update
            # hypervisor get stats
        }

    def get_host_from_icinga(self, *args):
        """
        Gets the host from Icinga. Not implemented yet
        :param args: Sink for all args
        :return: Raises a NotImplementedError
        """
        raise NotImplementedError("Getting hosts from Icinga is not implemented")

    def hypervisor_show(self, hypervisor):
        """
        Show Hypervisor information
        :param hypervisor (String): Hypervisor Name or ID
        :return: (status (Bool), reason/output (String/Dict))
        """
        try:
            hypervisor = self.conn.compute.find_hypervisor(
                hypervisor, ignore_missing=False
            )
        except ResourceNotFound as err:
            return False, f"IP not found {repr(err)}"
        return True, hypervisor

    def hypervisor_reboot(self, hypervisor, author, comment):
        """
        Reboot Hypervisor
        :param hypervisor (String): Hypervisor Name or ID
        :param author (String): Name of person authorising the reboot
        :param comment (String): Reason for reboot
        :return: (status (Bool), reason/output (String))
        """
        hypervisor_id = self.find_resource_id(
            hypervisor, self.conn.compute.find_hypervisor
        )
        if not hypervisor_id:
            return False, f"No Hypervisor found with Name or ID {hypervisor}"

        try:
            hypervisor = self.conn.compute.find_hypervisor(
                hypervisor_id, ignore_missing=False
            )
            host_name = hypervisor["hypervisor_hostname"]
            if not hypervisor:
                return (
                    False,
                    f"Malformed Message: Hypervisor with name {host_name} not found",
                )
        except ResourceNotFound as err:
            return False, f"Error finding hypervisor {err}"

        service = self.conn.compute.find_service("nova-compute", host=host_name)
        if service:
            if hypervisor["status"] == "enabled":
                server_list = [
                    server["name"]
                    for server in self.conn.list_servers(
                        filters={"all_tenants": True, "host": host_name, "limit": 10000}
                    )
                ]
                if not server_list:
                    self.conn.compute.disable_service(
                        service,
                        host_name,
                        service["binary"],
                        disabled_reason="disabled for reboot",
                    )
                else:
                    return (
                        False,
                        f"Servers {server_list} found active on Hypervisor {host_name} - aborting",
                    )

        start_time = datetime.datetime.now().timestamp() + 10
        end_time = start_time + 300

        if not self.schedule_icinga_downtime(
            host_name,
            start_time_unix=start_time,
            end_time_unix=end_time,
            start_time_str=None,
            end_time_str=None,
            author=author,
            comment=comment,
            is_flexible=False,
            flexible_duration=0,
        ):
            return False, "Icinga downtime request failed - aborting"
        return True, "Reboot Request Successful"

    # TODO wrap in struct
    # pylint: disable=too-many-arguments,too-many-locals
    def schedule_icinga_downtime(
        self,
        hypervisor,
        start_time_unix,
        end_time_unix,
        start_time_str,
        end_time_str,
        author,
        comment,
        is_flexible,
        flexible_duration,
    ):
        """
        Function to submit post request to schedule downtime on Icinga
            :param hypervisor: (String): Hypervisor Name or ID
            :param start_time_unix (Unix timestamp): start time for scheduled downtime (used openstack_resource default)
            :param end_time_unix (Unix timestamp): time when downtime scheduled to end (used openstack_resource default)
            :param start_time_str (String): time when downtime scheduled to start format:'%Y-%m-%d, %H:%M:%S'
            :param end_time_str (String): time when downtime scheduled to end format:'%Y-%m-%d, %H:%M:%S'
            :param author: (String): author/name of user who scheduled downtime
            :param comment: (String): reason/comment for downtime
            :param is_flexible: (Bool): set if downtime is flexible
            :param flexible_duration: (Int): time in seconds, how long the flexible duration lasts
            :return (status (Bool), reason/output (String))
        """

        hypervisor_id = self.find_resource_id(
            hypervisor, self.conn.compute.find_hypervisor
        )
        if not hypervisor_id:
            return False, f"No Hypervisor found with Name or ID {hypervisor}"

        host_name = self.conn.compute.find_hypervisor(hypervisor_id)[
            "hypervisor_hostname"
        ]
        if not self.get_host_from_icinga(host_name):
            return False, f"Host called {host_name} not found in Icinga"

        start_time = start_time_unix
        if start_time_str:
            start_time = datetime.datetime.strptime(
                start_time_str, "%Y-%m-%d, %H:%M:%S"
            ).timestamp()
            # convert to unix timestamp

        end_time = end_time_unix
        if end_time_str:
            start_time = datetime.datetime.strptime(
                start_time_str, "%Y-%m-%d, %H:%M:%S"
            ).timestamp()
            # convert to unix timestamp

        if start_time == "" or end_time == "":
            return False, "No end_time or start_time values given"

        if not end_time > start_time > datetime.datetime.now().timestamp():
            return (
                False,
                "Timestamps given for scheduling downtime are malformed - string needs to be YYYY-MM-DD, HH-MM-SS",
            )

        duration = flexible_duration if is_flexible else (end_time - start_time)
        request = requests.post(
            self.config.get("icinga_schedule_downtime_endpoint", None),
            headers={"Accept": "application/json"},
            auth=(
                self.config.get("icinga_username"),
                self.config.get("icinga_password"),
            ),
            verify=False,
            data=json.dumps(
                {
                    "type": "Host",
                    "filter": f'host.name=="{host_name}"',
                    "author": author,
                    "start_time": start_time,
                    "end_time": end_time,
                    "comment": comment,
                    "all_services": 1,
                    "duration": duration,
                    "fixed": not is_flexible,
                }
            ),
            timeout=300,
        )

        if request.ok:
            return (
                True,
                f"Downtime of Host {host_name} Scheduled For"
                f" For {datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d, %H:%M:%S')}"
                f" Until {datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d, %H:%M:%S')}"
                f" (Fixed: {not is_flexible}, Duration: {duration}",
            )
        return False, f"Downtime could not be scheduled: {request.text}"

    def remove_icinga_downtime(self, hypervisor):
        """
        Function called when message has REMOVE_DOWNTIME message type
            :param hypervisor (String): Hypervisor Name or ID
            :return (status (Bool), reason/output (String))
        """
        hypervisor_id = self.find_resource_id(
            hypervisor, self.conn.compute.find_hypervisor
        )
        if not hypervisor_id:
            return False, f"No Hypervisor found with Name or ID {hypervisor}"
        hypervisor_hostname = self.conn.compute.find_hypervisor(
            hypervisor_id, ignore_missing=False
        )["hypervisor_hostname"]

        if not self.get_host_from_icinga(hypervisor_hostname):
            return False, f"Host called {hypervisor_hostname} not found in Icinga"

        request = requests.post(
            self.config.get("icinga_remove_downtimes_endpoint", None),
            headers={"Accept": "application/json"},
            auth=(
                self.config.get("icinga_username"),
                self.config.get("icinga_password"),
            ),
            verify=False,
            data=json.dumps(
                {
                    "type": "Host",
                    "filter": f'host.name=="{hypervisor_hostname}"',
                }
            ),
            timeout=300,
        )
        if request.ok:
            return True, f"Downtimes of Host {hypervisor_hostname} Removed"
        return False, f"Downtimes could not be removed: {request.text}"

    def hypervisor_service_status(self, func, hypervisor, service_binary, **kwargs):
        """
        Function called when message involves changing the state of a service on a hypervisor
            :param func: service status change message type
            :param host_name (String): Name of hypervisor to change status for
            :param service_binary (String): Name of service on hypervisor to change status for
            :param kwargs: Misc properties/arguments
            :return (status (Bool), reason/output (String))
        """
        hypervisor_id = self.find_resource_id(
            hypervisor, self.conn.compute.find_hypervisor
        )
        if not hypervisor_id:
            return False, f"No Hypervisor found with Name or ID {hypervisor}"
        host_name = self.conn.compute.find_hypervisor(
            hypervisor_id, ignore_missing=False
        )["hypervisor_hostname"]
        service = self.conn.compute.find_service(service_binary, host=host_name)
        if not service:
            return (
                False,
                f"Service called {service_binary} not found on host {host_name}",
            )
        service_func = {
            "disable": lambda service, host_name, service_binary: self.conn.compute.disable_service(
                service, host_name, service_binary, kwargs["reason"]
            ),
            "enable": self.conn.compute.enable_service,
        }.get(func, None)

        service_func(service, host_name, service_binary)
        return True, "TODO: message"
