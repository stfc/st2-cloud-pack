"""
A python script to find empty hypervisors
"""
from openstack_api.openstack_hypervisor import OpenstackHypervisor
from openstack_api.openstack_connection import OpenstackConnection
from prettytable import PrettyTable

def run(cloud_account: str = "admin-openstack"):

    table = PrettyTable()        
    instance = OpenstackHypervisor()
    updateable_hvs = instance.get_all_empty_hypervisors(cloud_account)
    table.add_column("Hypervisor Name", updateable_hvs)
    print(table)
    print(len(updateable_hvs))

if __name__ == '__main__':
    run()
