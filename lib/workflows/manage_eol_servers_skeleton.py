
# ------------------------------------------------------------------------------ 

def find_eol_servers(wazuh_client, os_name, os_version):
    out = wazuh_client.get_servers_for_os(os_name, os_version)
    return out

def find_tagged_servers(conn):
    out = get_tagged_server_foo_fixme()
    return out

def _compare_lists(wazuh_l, tagged_l):
    wazuh_s = set(wazuh_l)
    tagged_s = set(tagged_l)
    only_wazuh = list(wazuh_s - tagged_s)
    only_tagged = list(tagged_s - wazuh_s)
    both = list(wazuh_s.intersection(tagged_s))
    return only_wazuh, only_tagged, both

# ------------------------------------------------------------------------------ 

def manage_new_eol_server(conn, server_id):
    set_tag_foo_fixme()
    set_metadata_foo_fixme() 
    username, email = find_user_info(server_id, conn._cloud_name)
    if not email:
        logger.error("there is no avaible information regarding the owner of Server %s", server_id)
    else:
        email 

def manage_new_eol_server_list(conn, only_wazuh_list):
    for server_id in only_wazuh_list:
        manage_new_eol_server(conn, server_id)

# ------------------------------------------------------------------------------ 

def manage_old_eol_server(conn, elog_client, server_id):
    metadata = get_metadata_foo_fixme()
    metadata_age = get_metadata_age_foo_fixme()
    if metadata_age < minimum_age: 
        logger.info("the user of server %s was notified %s ago, nothing to do yet", server_id, metadata_age)
    else:
        shutoff_server(server_id) 
        notify_user() 
        elog() 

def manage_old_eol_server_list(conn, elog_client, server_l):
    for server in server_l:
        manage_old_eol_server(conn, elog_client, server):

# ------------------------------------------------------------------------------ 

def manage_fixed_server(conn, elog_client, server_id):
    remove_metadata_foo_fixme()
    remove_tag_foo_fixme()
    elog()

def manage_fixed_server_list(conn, elog_client, server_l):
    for server in server_l:
        manage_fixed_server(conn, elog_client, server):

# ------------------------------------------------------------------------------ 
#
# main function
#
def eol_servers_workflow(conn, wazuh_client, elog_client, os_name, os_version):
    wazuh_server_list = find_eol_servers(wazuh_client, os_name, os_version)
    tagged_server_list = find_tagged_servers(conn)
    only_wazuh_list, only_tagged_list, both_list = _compare_list(wazuh_server_list, tagged_server_list)
    manage_new_eol_server_list(conn, only_wazuh_list)
    manage_old_eol_server_list(conn, elog_client, both_list)
    manage_fixed_server_list(conn, elog_client, only_tagged_list)
    





