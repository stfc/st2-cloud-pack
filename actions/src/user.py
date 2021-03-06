from openstack.exceptions import ResourceNotFound

from openstack_action import OpenstackAction


class User(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {"user_show": self.user_show, "user_get_email": self.user_get_email}

    def user_show(self, user, user_domain):
        """
        Show user information
        :param user: (String) ID or Name
        :param user_domain: (String) ID or Name
        :return: (status (Bool), reason/output (String/Dict))
        """

        # get domain id
        domain_id = self.find_resource_id(user_domain, self.conn.identity.find_domain)
        if not domain_id:
            return False, f"No domain found with Name or ID {user_domain}"
        try:
            user = self.conn.identity.find_user(user, domain_id=domain_id)
        except ResourceNotFound as err:
            return False, f"Finding User Failed {err}"
        return True, user

    def user_get_email(self, user, user_domain):
        """
        Get user email
        :param user: (String) ID or Name
        :param user_domain: (String) ID or Name
        :return: (status (Bool), reason/output (String/Dict))
        """
        res, output = self.user_show(user, user_domain)
        if not res:
            return False, output
        try:
            return True, output["email"] if output["email"] else "not found"
        except ResourceNotFound as err:
            return False, f"Finding User email Failed {err}"
