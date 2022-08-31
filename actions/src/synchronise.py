from openstack_api.openstack_connection import OpenstackConnection
from st2common.runners.base_action import Action

# pylint: disable=too-few-public-methods
class SyncAction(Action):
    # pylint: disable=arguments-differ
    def run(self, cloud, dupe_cloud):
        with OpenstackConnection(cloud) as conn:
            projects = conn.list_projects()
        for i in projects:
            if i["name"] != "admin":  # Check if project is the admin project
                with OpenstackConnection(cloud) as conn:
                    project_users = conn.list_role_assignments(
                        filters={
                            "project": i["id"]
                        }  # Get list of users with access to project
                    )
                    stfc_users = []
                    for user in project_users:
                        user_info = conn.identity.get_user(user["user"])
                        if user_info["domain_id"] == "5b43841657b74888b449975636082a3f":
                            print(f"{user_info['name']} is in stfc")
                            stfc_users.append(
                                user_info
                            )  # Add user to list, so Can add them to project later
                with OpenstackConnection(dupe_cloud) as conn:
                    dev_proj = conn.list_projects()
                    if not any(
                        i["name"] in d.values() for d in dev_proj
                    ):  # Loop through all values and check if project is there
                        self._create_project(  # Start project creation
                            dupe_cloud=dupe_cloud, original=i
                        )

            self._grant_roles(
                cloud=cloud, dupe_cloud=dupe_cloud, proj_users=stfc_users, project=i
            )  # Give correct roles to users
            print("-------------")

    def _create_project(self, dupe_cloud, original):
        with OpenstackConnection(dupe_cloud) as conn:
            conn.create_project(name=str(original["name"]), domain_id="default")
            print(f"Created project {original['name']}")

    def _grant_roles(self, cloud, dupe_cloud, proj_users, project):
        with OpenstackConnection(dupe_cloud) as dev:
            dev_proj = dev.get_project(name_or_id=project["name"])
            stfc_domain = dev.identity.find_domain(name_or_id="stfc")

        print(f"Setting up roles on {dev_proj['name']}")  # testing
        with OpenstackConnection(cloud) as conn:
            for i in proj_users:
                roles = conn.identity.role_assignments_filter(
                    user=i["id"], project=project["id"]
                )
                for role in roles:
                    with OpenstackConnection(dupe_cloud) as dev:
                        dev_role = dev.get_role(name_or_id=role["name"])
                        dev_user = dev.get_user(
                            name_or_id=i["name"],
                            domain_id="b6be97c034e04e9b9b1d50ccea33a5df",
                        )
                        dev_roles = dev.identity.role_assignments_filter(
                            user=dev_user["id"], project=dev_proj["id"]
                        )
                        if not any(
                            role["name"] in dev_role.values() for dev_role in dev_roles
                        ):
                            dev.grant_role(
                                name_or_id=dev_role["id"],
                                project=dev_proj,
                                user=dev_user,
                                domain=stfc_domain["id"],
                            )
                            print(
                                f"{dev_role['name']} granted to {dev_user['name']} on project {dev_proj['name']}"
                            )
                        else:
                            print(
                                f"{dev_user['name']} already has role {dev_role['name']} in project {dev_proj['name']}"
                            )


# Do not sync admin project and IRIS IAM accounts, just FedID
# Just sync projects with names and accounts that have access.
