import logging
import random
import re

from openstack.connection import Connection
from apis.openstack_api.openstack_hypervisor import get_available_flavors
from apis.openstack_api.openstack_server import build_server, delete_server

logger = logging.getLogger(__name__)


def create_test_server_single_hypervisor(
    conn: Connection,
    hypervisor_name: str,
    test_all_flavors: bool,
    delete_on_failure: bool,
) -> None:
    """
    Create a test server on a hypervisor, option to test all possible flavors avaliable to the hypervisor

    :param conn: openstack connection object
    :type conn: Connection
    :param hypervisor_name: Hostname of the hypervisor
    :type hypervisor_name: str
    :param test_all_flavors: Option to test all possible flavors avaliable to the hypervisor
    :type test_all_flavors: bool
    :return: None
    :rtype: None
    """
    # 1st we ensure the hypervisor name is correct
    # remove potential leading/trailing whitespaces
    hypervisor_name = hypervisor_name.strip()
    if not hypervisor_name:
        raise ValueError("Hypervisor hostname is empty")
    # check no special characters are included
    pattern = re.compile(r"^[A-Za-z0-9._-]+$")
    # Compile a regular expression that allows:
    # - letters (a–z, A–Z)
    # - digits (0–9)
    # - dot (.)
    # - underscore (_)
    # - dash (-)
    if not pattern.fullmatch(hypervisor_name):
        raise ValueError("Hypervisor hostname cannot include special characters")
    # if everything is OK with the hostname we can proceed
    flavors = get_available_flavors(conn, hypervisor_name)
    logger.info("Flavors avaliable to %s: %s", hypervisor_name, flavors)
    if not test_all_flavors:
        flavors = [random.choice(flavors)]
    for flavor in flavors:
        logger.info("Building flavor: %s", flavor)
        server = build_server(
            conn,
            "stackstorm-test-server",
            flavor,
            "ubuntu-jammy-22.04-nogui",
            "Internal",
            hypervisor_name,
            delete_on_failure,
        )
        logger.info("✔ Successfully built flavor: %s", flavor)
        delete_server(conn, server.id)
        logger.info("Successfully deleted flavor: %s", flavor)


def _str_to_list(hypervisor_names):
    """
    convert a single string with hypervisor names into a python list

    :param hypervisor_names: A string containing one or more hypervisor names
                            separated by commas or colons.
    :type hypervisor_names: str

    :return: A list of hypervisor names with whitespace stripped and empty
            entries removed.
    :rtype: list[str]

    :raises ValueError: If the input string contains both commas and colons
                       as delimiters.
    """
    # we allow the hostnames to be split by either comma (,) or colon (:)
    # but only one, not both
    has_colon = ":" in hypervisor_names
    has_comma = "," in hypervisor_names
    if has_colon and has_comma:
        raise ValueError(
            "All hostnames must be split by either only commas or only colons, not both"
        )
    # we convert the input into a proper list
    delimiter = ":" if has_colon else ","
    hv_name_l = [
        name.strip() for name in hypervisor_names.split(delimiter) if name.strip()
    ]
    return hv_name_l


def create_test_server(
    conn: Connection,
    hypervisor_names: str,
    test_all_flavors: bool,
    delete_on_failure: bool,
) -> None:
    """
    Create a test server on one or more hypervisors

    :param conn: openstack connection object
    :type conn: Connection
    :param hypervisor_names: Hostnames of the hypervisors
    :type hypervisor_name: str
    :param test_all_flavors: Option to test all possible flavors avaliable to the hypervisor
    :type test_all_flavors: bool
    :return: None
    :rtype: None
    """
    # 1st we convert the hypervisor_names string into a list
    hv_name_l = _str_to_list(hypervisor_names)
    # now we loop over all individual hypervisor names
    # and call the function that checks the VM creation
    for hv_name in hv_name_l:
        create_test_server_single_hypervisor(
            conn, hv_name, test_all_flavors, delete_on_failure
        )
