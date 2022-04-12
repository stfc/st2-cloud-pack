from openstack.exceptions import ResourceNotFound

from openstack_action import OpenstackAction


class FloatingIP(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {
            "floating_ip_create": self.floating_ip_create,
            "floating_ip_delete": self.floating_ip_delete,
            "floating_ip_show": self.floating_ip_show
            # floating_ip_update
        }

    def floating_ip_show(self, ip_addr):
        """
        Show floating ip_addr information
        :param ip_addr: floating ip_addr id (String)
        :return: (status (Bool), reason/output (String/Dict))
        """
        try:
            ip_addr = self.conn.identity.find_ip(ip_addr, ignore_missing=False)
        except ResourceNotFound as err:
            return False, f"IP not found:\n{err}"
        return True, ip_addr

    def floating_ip_delete(self, ip_addr):
        """
        Delete floating ip_addr
        :param ip_addr: ip_addr id
        :return: (status (Bool), reason/output (String/Dict))
        """
        raise NotImplementedError("Deleting floating IPs are not supported")

    def floating_ip_create(self, network, project, number_to_create):
        """
        Create floating IPs for a project
        :param network (String): ID or Name,
        :param project (String): ID or Name,
        :param number_to_create (Int): Number of floating ips to create
        :return: (status (Bool), reason (String))
        """
        # get network id
        network_id = self.find_resource_id(network, self.conn.network.find_network)
        if not network_id:
            return False, f"Network not found with Name or ID {network}"

        # get project id:
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, f"Project not found with Name or ID {project}"

        ip_output = [
            self.conn.network.create_ip(
                project_id=project_id, floating_network_id=network_id
            )
            for _ in range(number_to_create)
        ]
        return True, ip_output
