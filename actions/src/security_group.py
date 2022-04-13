import os
from subprocess import Popen, PIPE

from openstack.exceptions import ResourceNotFound, ConflictException
from openstack_action import OpenstackAction

SOURCECMD = "source /etc/openstack/openrc/admin-openrc.sh;"


class SecurityGroup(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {
            "security_group_create": self.security_group_create,
            "security_group_rule_create": self.security_group_rule_create,
            "security_group_show": self.security_group_show,
            "security_group_list": self.security_group_list
            # security_group_delete
            # security_group_update
        }

    def security_group_create(self, project, **security_group_kwargs):
        """
        Create a Security Group for a Project
        :param project: (String) ID or Name,
        :param security_group_kwargs - see action definintion yaml file for details
        :return: (status (Bool), reason (String))
        """
        # get project id
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, f"Project not found with Name or ID {project}"

        try:
            security_group = self.conn.network.create_security_group(
                project_id=project_id, **security_group_kwargs
            )
        except ResourceNotFound as err:
            return False, f"Security Group Creation Failed {err}"
        return True, security_group

    def security_group_show(self, project, security_group):
        """
        Show a security group
        :param project: ID or Name,
        :param security_group: ID or Name
        :return: (status (Bool), reason (String))
        """

        # if project specified - show security group info for that project
        if project:
            project_id = self.find_resource_id(project, self.conn.identity.find_project)
            if not project_id:
                return False, f"Project not found with Name or ID {project}"

            try:
                security_group = self.conn.network.find_security_group(
                    security_group, project_id=project_id
                )
            except ResourceNotFound as err:
                return False, f"Finding Project Failed {err}"
        else:
            try:
                security_group = self.conn.network.find_security_group(security_group)
            except ResourceNotFound as err:
                return False, f"Finding Project Failed {err}"
        return True, security_group

    def security_group_list(self, project):
        """
        List Security groups for a project
        :param project:(String) Name or ID
        :return: (status (Bool), reason (String))
        """
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, f"Project not found with Name or ID {project}"

        # needs to be called when creating new project, openstacksdk fails to find security groups unless this is called
        with (
            Popen(
                SOURCECMD
                + f"openstack security group list --project {project_id} -f json",
                shell=True,
                stdout=PIPE,
                env=os.environ.copy(),
            )
        ) as process_handle:
            _ = process_handle.communicate()[0]

        try:
            security_groups = self.conn.network.security_groups(project_id=project_id)
            all_groups = []
            for group in security_groups:
                all_groups.append(group)
        except ResourceNotFound as err:
            return False, f"Listing Security Groups Failed {err}"
        return True, all_groups

    def security_group_rule_create(
        self, security_group, project, dst_port, **security_group_kwargs
    ):
        """
        Creature security group rule
        :param security_group: (String) Name or ID
        :param project: (String) Name or ID,
        :param dst_port: (String: <Int>:<Int>) Min and Max port range,
        :param security_group_kwargs: other_args - see action definintion yaml file for details
        :return: (status (Bool), reason (String))
        """

        # get project id
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, f"Project not found with Name or ID {project}"

        # get security group id
        security_group_id = self.find_resource_id(
            security_group, self.conn.network.find_security_group, project_id=project_id
        )
        if not security_group_id:
            return (
                False,
                f"Security group not found with Name or ID {security_group} for Project {project}",
            )

        # get min and max port ranges
        if dst_port:
            port_range_min, port_range_max = dst_port.split(":")
        else:
            port_range_min, port_range_max = None, None

        try:
            security_group_rule = self.conn.network.create_security_group_rule(
                project_id=project_id,
                security_group_id=security_group_id,
                port_range_max=port_range_max,
                port_range_min=port_range_min,
                **security_group_kwargs,
            )
        except ConflictException:
            return (
                True,
                f"Security Group Rule direction={security_group_kwargs['direction']},"
                f" ether_type={security_group_kwargs['ether_type']},"
                f" protocol=security_group_kwargs['protocol'],"
                f" remote_ip_prefix={security_group_kwargs['remote_ip_prefix']},"
                f" dst_port={port_range_max}:{port_range_min}"
                f" exist for project {project_id}",
            )
        except ResourceNotFound as err:
            return False, f"Security group rule creation failed {err}"
        return True, security_group_rule
