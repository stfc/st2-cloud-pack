# from typing import Optional

# import openstackquery
# from openstack.connection import Connection
# from openstack_api.openstack_server import migrate_server, snapshot_server


# def server_migration(
#     conn: Connection,
#     cloud_account: str,
#     server_id: str,
#     destination_host: Optional[str] = None,
# ) -> None:
#     """Docstring for server_migration

#     :param cloud_account: Cloud account to use for openstack interaction
#     :type cloud_account: str
#     :param server_id: Server ID of server to migrate
#     :type server_id: str
#     :param destination_host: Optional, host to migrate server to
#     :type destination_host: str
#     :param live: True to use live migration
#     :type live: bool
#     """

#     # Determine the status of the server
#     query = getattr(openstackquery, "ServerQuery")()
#     query.select("server_status")
#     query.where(
#         preset="any_in",
#         prop="server_id",
#         values=[server_id],
#     )
#     query.run(cloud_account, all_projects=True, as_admin=True)
#     status = query.to_props()[0].get("server_status")
#     if status == "ACTIVE":
#         live_migration = True
#         print(f"live migration: {live_migration}")
#         snapshot_server(conn, server_id)
#         migrate_server(
#             conn, server_id=server_id, dest_host=destination_host, live=live_migration
#         )
#     elif status == "SHUTOFF":
#         live_migration = False
#         print(f"live migration: {live_migration}")
#         snapshot_server(conn, server_id)
#         migrate_server(
#             conn, server_id=server_id, dest_host=destination_host, live=live_migration
#         )
#     else:
#         print("Status not SHUTOFF or ACTIVE - ERROR!")
