
def find_eol_servers(wazuh_client, os_name, os_version):
    out = wazuh_client.get_servers_for_os(os_name, os_version)
    return out


def manage_new_eol_server(conn, server_id):
    set_metadata_foo_fixme() # FIXME !!!
    username, email = find_user_info(server_id, conn._cloud_name)
    if not email:
        logger.error("there is no avaible information regarding the owner of Server %s", server_id)
    else:
        email # FIXME !!!


def manage_old_eol_server(conn, elog_client, server_id, metadata):
    metadata_age = ... # FIXME !!! 
    if metadata_age < minimum_age: # FIXME !!!
        logger.info("the user of server %s was notified %s ago, nothing to do yet", server_id, metadata_age)
    else:
        shutoff_server(server_id) # FIXME !!!
        notify_user() # FIXME !!!
        elog() # FIXME !!!


def manage_eol_server(conn, elog_client, server_id):
    metadata = get_metadata_foo_fixme() # FIXME !!!
    if not metadata:
        manage_new_eol_server(conn, server_id)
    else:
        manage_old_eol_server(conn, elog_client, server_id)


def eol_servers_workflow(conn, wazuh_client, elog_client, os_name, os_version):
    server_list = find_eol_servers(wazuh_client, os_name, os_version)
    for server in server_list:
        manage_eol_server(conn, elog_client, server)
