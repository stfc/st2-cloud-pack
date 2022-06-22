from openstack_api.openstack_connection import OpenstackConnection
from st2common.runners.base_action import Action


class SyncAction(Action):
    def run(self, cloud, dupe_cloud):
        with OpenstackConnection(cloud) as conn:
            projects = conn.list_projects()
            count = 1
        for i in projects:
            if count == 10:
                break

            if i["name"] != "admin":
                with OpenstackConnection(cloud) as conn:
                    project_users = conn.list_role_assignments(
                        filters={"project": i["id"]}
                    )
                    for y in project_users:
                        yuser = conn.identity.get_user(y["user"])
                        if yuser["domain_id"] == "5b43841657b74888b449975636082a3f":
                            print(yuser["name"])
                with OpenstackConnection(dupe_cloud) as conn:
                    dev_proj = conn.list_projects()
                    if not any(i["name"] in d.values() for d in dev_proj):
                        print(i["name"])
                        self._create_project(
                            dupe_cloud=dupe_cloud,
                            original=i,
                            project_users=project_users,
                        )
                        count += 1

    def _create_project(self, dupe_cloud, original, project_users):
        with OpenstackConnection(dupe_cloud) as conn:
            # conn.create_project(
            #    name= str(original["name"]),
            #    domain_id= "default"
            # )
            print(f"(Didn't) Created project {original['name']}")

        # for i in users:


sync = SyncAction()

sync.run(cloud="openstack", dupe_cloud="dev")

# Do not sync admin project and IRIS IAM accounts, just FedID
# Just sync projects with names and accounts that have access.

# with OpenstackConnection("dev") as conn:
#    print(dir(conn.identity))
