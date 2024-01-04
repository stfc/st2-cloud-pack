import openstack
from openstack_query.api.query_objects import (
    FlavorQuery,
    AggregateQuery,
    HypervisorQuery,
    ImageQuery,
)


# def get_hv_objects_from_names(cloud_account, host_name_list):
#     hv_query = HypervisorQuery()
#     hv_query.where("any_in", "name", values=host_name_list)
#     hv_query.run(cloud_account)
#     return hv_query.to_objects()


def create_vms(cloud_account, hv_object_list, flavor_id, image_id):
    conn = openstack.connect(cloud_account)
    network = conn.network.find_network(
        "fa2f5ebe-d0e0-4465-9637-e9461de443f1", ignore_missing=False
    )
    for hv in hv_object_list:
        try:
            conn.compute.create_server(
                **{
                    "name": f"build_test_{hv}",
                    "imageRef": image_id,
                    "flavorRef": flavor_id,
                    "networks": [network],
                    "hypervisor": hv,
                    "openstack_api_version": "2.79",
                }
            )
            return True, "Server creation successful"
        except openstack.exceptions.ResourceNotFound as err:
            return False, f"Openstack error: {repr(err)}"


def main(cloud_account, flavor_name):
    security_group_id = "a64e8c5d-b99b-4f2b-96ea-2cd3da82c29b"  # default security group in prod-cloud admin project
    network_id = (
        "5be315b7-7ebd-4254-97fe-18c1df501538"  # Internal network id from prod-cloud
    )
    q1 = FlavorQuery()
    q1.select("hosttype", "id")
    q1.where("equal_to", "name", value=flavor_name)
    q1.run(cloud_account)
    searched_hosttype = q1.to_props(flatten=True)["flavor_hosttype"][0]
    flavor_id = q1.to_props(flatten=True)["flavor_id"][0]

    q2 = AggregateQuery()
    q2.select("hosts")
    q2.where("equal_to", "hosttype", value=searched_hosttype)
    q2.run(cloud_account)
    all_host_groups = q2.to_props(flatten=True)["aggregate_host_ips"]

    q3 = ImageQuery()
    q3.select("id")
    imagename = "ubuntu-focal-20.04-nogui"
    q3.where("equal_to", "name", value=imagename)
    q3.where("equal_to", "status", value="active")
    q3.run(cloud_account, as_admin=True, all_projects=True)
    image_id = q3.to_props(flatten=True)["image_id"][0]

    for host_group in all_host_groups:
        create_vms(cloud_account, host_group, flavor_id, image_id)


if __name__ == "__main__":
    main("dev", "l3.nano")
