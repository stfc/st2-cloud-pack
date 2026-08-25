from datetime import datetime
import logging
import time
from typing import Optional, List, Dict
from openstack.connection import Connection
from openstack.compute.v2.image import Image
from openstack.compute.v2.server import Server
from openstack.exceptions import (
    BadRequestException,
    ResourceFailure,
    ResourceTimeout,
    NotFoundException,
    ResourceNotFound,
    SDKException,
)

NOVA_MICROVERSION_FOR_TAGS = "2.26"


logger = logging.getLogger(__name__)


def can_be_migrated(server: Server):
    if server.flavor.name.startswith("g-") or server.flavor.name.startswith("f-"):
        raise ValueError(
            f"Attempted to move GPU or FPGA flavor, {server.flavor.name}, which is not allowed!"
        )


def _cold_migration(
    conn: Connection,
    server: Server,
    dest_host: Optional[str] = None,
) -> None:
    conn.compute.migrate_server(server=server.id, host=dest_host)

    # Using conn.compute.wait_for_server will wait even if our migration transitions to error
    # causing a hang until timeout so we must wait for the migration then wait for OpenStack
    # to update the status after....
    wait_for_migration_status(conn, server.id, "finished")

    # We're just waiting for Nova to update as the migration has completed here
    conn.compute.wait_for_server(server, status="VERIFY_RESIZE", wait=10)

    if server.status.casefold() != "VERIFY_RESIZE".casefold():
        raise RuntimeError(
            f"Migration caused VM to enter unexpected state {server.status}"
            " instead of 'VERIFY_RESIZE'."
        )

    logger.info("Confirming resize for %s", server.id)
    conn.compute.confirm_server_resize(server.id)


def _live_migration(
    conn: Connection,
    server: Server,
    dest_host: Optional[str] = None,
) -> None:
    conn.compute.live_migrate_server(
        server=server.id, host=dest_host, block_migration=True
    )
    wait_for_migration_status(conn, server.id, "completed")


def snapshot_and_migrate_server(
    conn: Connection,
    server_id: str,
    snapshot: bool,
    live_migration: bool,
    dest_host: Optional[str] = None,
) -> None:
    """
    Optionally snapshot a server and then migrate it to a new host
    :param conn: Openstack Connection
    :param server_id: Server ID to migrate
    :param server_status: Status of machine to migrate - must be ACTIVE or SHUTOFF
    :param flavor_name: Server flavor name
    :param live_migration: decides if an ACTIVE Server should go under Cold Migration or Live Migration
    :param dest_host: Optional host to migrate to, otherwise chosen by scheduler
    """
    server = conn.compute.get_server(server_id)
    if snapshot:
        snapshot_server(conn=conn, server_id=server_id)
        time.sleep(10)  # Ensure server task status has updated after snapshot
    logger.info("Migrating server: %s", server.id)

    server_status = server.status.casefold()

    match server_status:
        case "shutoff":
            _cold_migration(conn, server, dest_host)
        case "active":
            if live_migration:
                can_be_migrated(server)
                _live_migration(conn, server, dest_host)
            else:
                _cold_migration(conn, server, dest_host)
        case _:
            raise ValueError(
                f"Server status: {server.status}. The server must be ACTIVE or SHUTOFF to be migrated"
            )
    logger.info("Migration completed of server: %s", server.id)


def snapshot_server(conn: Connection, server_id: str) -> Image:
    """
    Creates a snapshot image of a server
    :param conn: Openstack connection
    :param server_id: ID of server to snapshot
    :return: Snapshot Image
    """
    current_time = datetime.now().strftime("%d-%m-%Y-%H%M")

    server = conn.compute.find_server(server_id, all_projects=True)
    logger.info("Starting snapshot of server: %s", server.id)
    image = conn.compute.create_server_image(
        server=server_id,
        name=f"stackstorm-{server_id}-{current_time}",
        wait=True,
        timeout=21600,  # 6 Hours
    )
    wait_for_image_status(conn, image, "active")
    # Make VM's project image owner
    conn.image.update_image(image, owner=server.project_id)
    logger.info("Completed snapshot of server: %s", server.id)
    return image


def wait_for_image_status(conn: Connection, image, status, interval=5, timeout=3600):
    """
    Waits for the status of the image to be the selected status
    :param conn: Openstack connection
    :param image: The Image object
    :param status: The status of the image that is required
    :param interval:How long to wait between checks
    :param timeout: Timeout of the function
    """
    if image.status == status:
        return image
    start_time = time.time()
    while time.time() - start_time < timeout:
        logger.info("Status of image %s: %s", image.id, image.status)
        image = conn.image.get_image(image.id)
        if image.status == status:
            return image
        if image.status == "error":
            raise ResourceFailure(f"Image {image.name} failed to upload.")
        time.sleep(interval)
    raise ResourceTimeout(f"Timeout waiting for image {image.name} to become {status}.")


def wait_for_migration_status(
    conn: Connection, server_id, status, interval=5, timeout=3600
):
    """
    Waits for the status of the migration to be the selected status
    :param conn: Openstack connection
    :param server_id: The ID of the server where the migrations are from
    :param status: The status of the migration that is required
    :param interval:How long to wait between checks
    :param timeout: Timeout of the function
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            migration = next(conn.compute.migrations(instance_uuid=server_id))
        except StopIteration:
            logger.info("No migration details available for %s yet", server_id)
            time.sleep(interval)
            continue

        logger.info("Status of migration of server %s: %s", server_id, migration.status)
        if migration.status == status:
            return migration
        if migration.status in ["error", "failed"]:
            raise ResourceFailure(migration)
        time.sleep(interval)
    raise ResourceTimeout(f"Timeout waiting for migration to become {status}.")


def build_server(
    conn: Connection,
    server_name: str,
    flavor_name: str,
    image_name: str,
    network_name: str,
    hypervisor_hostname: Optional[str] = None,
    delete_on_failure: Optional[bool] = False,
) -> Server:
    """
    Builds a server, with option to specify a hypervisor

    :param conn: openstack connection object
    :type conn: Connection
    :param server_name: Name of server
    :type server_name: str
    :param flavor_name: Flavor to use for server
    :type flavor_name: str
    :param image_name: Image to use for server
    :type image_name: str
    :param network_name: Network name for server
    :type network_name: str
    :param hypervisor_hostname: Optional, hypervisor to build server on
    :type hypervisor_hostname:
    :return: Server instance
    :rtype: Server
    """
    flavor = conn.compute.find_flavor(flavor_name)
    image = conn.image.find_image(image_name)
    network = conn.network.find_network(network_name)

    server = conn.compute.create_server(
        **{
            "name": server_name,
            "imageRef": image.id,
            "flavorRef": flavor.id,
            "networks": [{"uuid": network.id}],
            "host": hypervisor_hostname,
            "openstack_api_version": "2.74",
        }
    )
    logger.info("Building server: %s", server.id)
    try:
        conn.compute.wait_for_server(
            server, status="ACTIVE", failures=None, interval=5, wait=3600
        )
    except (ResourceTimeout, ResourceFailure) as e:
        if delete_on_failure:
            conn.compute.delete_server(server, force=True)
        raise ResourceFailure(server.fault) from e
    logger.info("Built server: %s", server.id)
    return server


def delete_server(
    conn: Connection, server_id: str, force: Optional[bool] = False
) -> None:
    """
    Delete a server

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: ID of server to delete
    :type server_id: str
    :param force: Option to force delete server
    :type force: bool
    :return: None
    :rtype: None
    """
    server = conn.compute.find_server(server_id)
    logger.info("Deleting server: %s", server.id)
    conn.compute.delete_server(server, force)

    conn.compute.wait_for_delete(server, interval=5, wait=3600)
    logger.info("Deleted server: %s", server.id)


def shutoff_server(conn: Connection, server_id: str) -> None:
    """
    Shutoff a server

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: ID of server to delete
    :type server_id: str
    :return: None
    :rtype: None
    """
    server = conn.compute.find_server(server_id)
    logger.info("Attempt to shutoff server %s", server.id)
    if server.status.upper() == "ACTIVE":
        logger.info("Shutting off server: %s", server.id)
        conn.compute.stop_server(server)
        logger.info("Waiting for server to shut off: %s", server.id)
        try:
            conn.compute.wait_for_status(server, status="SHUTOFF")
        except ResourceFailure as ex:
            logger.error("server %s is in ERROR status : %s", server.id, ex)
            raise ex
        logger.info("server is shut off: %s", server.id)
    elif server.status.upper() in ["SHUTOFF", "STOPPED"]:
        logger.info(
            "Server %s is in status %s, nothing to do",
            server.id,
            server.status,
        )
    else:
        logger.info(
            "Server %s is in status %s, cannot perform standard shutdown",
            server.id,
            server.status,
        )


def shutoff_server_list(conn: Connection, server_id_list: List[str]) -> None:
    """
    Shutoff a list of servers

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id_list: List of ID of servers to delete
    :type server_id: List[str]
    :return: None
    :rtype: None
    """
    for server_id in server_id_list:
        shutoff_server(conn, server_id)


def add_metadata_to_server(conn: Connection, server_id: str, properties: Dict) -> None:
    """
    Add new key:values pair to the Server metadata

    The metadata is the field displayed as "properties"
    when running "openstack server show" commands

    Note, if a key in properties already exists in the Servers metadata,
    it will be overridden with the new value

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: the ID of the Server object
    :type server_id: str
    :param properties: the new properties to add to the server metadata
    :type properties: dictionary
    """
    logger.info(
        "calling function add_metadata for server %s to add properties %s",
        server_id,
        properties,
    )
    server = conn.compute.find_server(server_id, all_projects=True)
    conn.compute.set_server_metadata(server, **properties)
    logger.info("new properties added to server")


def delete_metadata_from_server(
    conn: Connection, server_id: str, properties: List
) -> None:
    """
    Remove some key:values pair from the Server metadata

    The metadata is the field displayed as "properties"
    when running "openstack server show" commands

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: the ID of the Server object
    :type server_id: str
    :param properties: the properties to remove from the server metadata
    :type properties: list
    """
    logger.info(
        "calling function delete_metadata for server %s to remove properties %s",
        server_id,
        properties,
    )
    server = conn.compute.find_server(server_id, all_projects=True)
    conn.compute.delete_server_metadata(server, keys=properties)
    logger.info("properties removed from server")


def add_tag_to_server(conn: Connection, server_id: str, tag: str) -> None:
    """
    Adds a tag to a Server

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: ID of the Server
    :type server_id: str
    :param tag: the tag to be added to the Server
    :type tag: str
    :return: None
    :rtype: None
    """
    logger.info("adding tag %s to server %s", tag, server_id)
    current_microversion = conn.compute.default_microversion
    # we need a very specific NOVA version for this action
    logger.info("setting temporarily NOVA microversion")
    conn.compute.default_microversion = NOVA_MICROVERSION_FOR_TAGS
    conn.compute.add_tag_to_server(server_id, tag)
    # restore the NOVA version
    conn.compute.default_microversion = current_microversion
    logger.info("restoring NOVA microversion")
    logger.info("tag %s added to server %s", tag, server_id)


def remove_tag_from_server(conn: Connection, server_id: str, tag: str) -> None:
    """
    Removes a tag from a Server

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: ID of the Server
    :type server_id: str
    :param tag: the tag to be removed from the Server
    :type tag: str
    :return: None
    :rtype: None
    """
    logger.info("removing tag %s from server %s", tag, server_id)
    current_microversion = conn.compute.default_microversion
    # we need a very specific NOVA version for this action
    logger.info("setting temporarily NOVA microversion")
    conn.compute.default_microversion = NOVA_MICROVERSION_FOR_TAGS
    try:
        conn.compute.remove_tag_from_server(server_id, tag)
    except NotFoundException:
        logger.error("server %s does not have tag %s", server_id, tag)
    # restore the NOVA version
    conn.compute.default_microversion = current_microversion
    logger.info("restoring NOVA microversion")
    logger.info("tag %s removed from server %s", tag, server_id)


def find_servers_with_tag(conn: Connection, tag: str) -> List[str]:
    """
    find the list of Servers with a given tag

    :param conn: openstack connection object
    :type conn: Connection
    :param tag: the tag to search for servers by
    :type tag: str
    :return: the list of Servers with the tag
    :rtype: List[str]
    """
    logger.info("searching for all servers with tag %s", tag)
    servers = conn.compute.servers(all_projects=True, tags=tag)
    out = [server.id for server in servers]
    logger.info("found %s servers with tag %s", len(out), tag)
    return out


def get_server_owner_email(conn: Connection, server_id: str) -> str:
    """
    Returns, when possible, the email of User who instantiated a Server

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: the ID of the Server
    :type server_id: str
    :return: the email of the User
    :rtype: str
    :raises ResourceNotFound: if the Server does not have User information
        or the user does not exist
    :raises openstack.exceptions.SDKException:
        if the User exists but does not expose a valid name attribute
    """
    logger.info("fetching the email of the owner of server %s", server_id)
    server = conn.compute.get_server(server_id)

    user_id = getattr(server, "user_id", None)
    if not user_id:
        error_msg = f"Server '{server_id}' does not have an associated user_id."
        logger.critical(error_msg)
        raise ResourceNotFound(error_msg)

    user = conn.identity.get_user(user_id)
    if not user:
        error_msg = (
            f"User '{user_id}' referenced by server '{server_id}' was not found."
        )
        logger.critical(error_msg)
        raise ResourceNotFound(error_msg)

    user_email = getattr(user, "email", None)
    if not user_email:
        error_msg = f"User '{user_id}' referenced by server '{server_id}' does not provide for an email."
        logger.critical(error_msg)
        raise SDKException(error_msg)

    logger.info(
        "returning email address %s for the owner of server %s", user_email, server_id
    )
    return user_email


def admin_lock_server(conn: Connection, server_id: str, reason: str) -> str:
    """
    admin lock a Server so the User cannot change its state.
    For example, when we want to SHUTOFF the Server and only an admin
    should be able to restart it.

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: the ID of the Server
    :type server_id: str
    :param reason: the reason for the admin lock
    :type reason: str
    """
    logger.info("admin locking server %s for reason %s", server_id, reason)
    if len(reason) < 255:
        conn.compute.lock_server(server_id, reason)
    else:
        error_msg = f"reason '{reason}' exceeds the limit of 255 characters"
        logger.critical(error_msg)
        raise BadRequestException(error_msg)
    logger.info("server %s admin locked", server_id)


def admin_unlock_server(conn: Connection, server_id: str) -> str:
    """
    remove the admin lock set to a  Server

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: the ID of the Server
    :type server_id: str
    """
    logger.info("admin unlocking server %s", server_id)
    conn.compute.unlock_server(server_id)
    logger.info("server %s admin unlocked", server_id)
