# Hypervisors
Hypervisors refer to the software that creates and runs virtual machines (VMs) (Also known in Openstack as Servers).
The physical device the Hypervisor runs on is known as the host.
See [Openstack Docs](https://docs.openstack.org/api-ref/compute/#hypervisors-os-hypervisors) for more info

**NOTE: `HypervisorQuery` will only work with admin credentials - set by `clouds.yaml`**

## Querying

To Query for Hypervisors using the Query Library, you can import `HypervisorQuery()` like so:

```python
from openstack_query import HypervisorQuery
```

`HypervisorQuery()` can then be used to setup and run queries - see [API.md](../API.md) for details on API calls

## Properties

The Valid property enum for `HypervisorQuery` is `HypervisorProperties`. You can import `HypervisorProperties` like so:

```python
from enums.query.props.hypervisor_properties import HypervisorProperties
```

`HypervisorProperties` exposes the following properties:

| Property Enum                 | Type     | Aliases (case-insensitive)         | Description                                                     |
|-------------------------------|----------|------------------------------------|-----------------------------------------------------------------|
| HYPERVISOR_CURRENT_WORKLOAD   | `int`    | "current_workload", "workload"     | The number of tasks the hypervisor is responsible for           |
| HYPERVISOR_DISK_FREE          | `int`    | "local_disk_free", "free_disk_gb"  | The local disk space remaining on this hypervisor(in GiB)       |
| HYPERVISOR_DISK_SIZE          | `int`    | "local_disk_size", "local_gb"      | Total local disk size on this hypervisor (in GiB).              |
| HYPERVISOR_DISK_USED          | `int`    | "local_disk_used", "local_gb_used" | The local disk space allocated on this hypervisor(in GiB)       |
| HYPERVISOR_ID                 | `string` | "id", "uuid", "host_id"            | ID of the Hypervisor                                            |
| HYPERVISOR_IP                 | `string` | "ip", "host_ip"                    | The IP address of the hypervisor’s host                         |
| HYPERVISOR_MEMORY_FREE        | `int`    | "memory_free", "free_ram_mb"       | The free RAM on this hypervisor(in MiB).                        |
| HYPERVISOR_MEMORY_SIZE        | `int`    | "memory_size", "memory_mb"         | Total RAM size for this hypervisor(in MiB).                     |
| HYPERVISOR_MEMORY_USED        | `int`    | "memory_used", "memory_mb_used"    | RAM currently being used on this hypervisor(in MiB).            |
| HYPERVISOR_NAME               | `string` | "name", "host_name"                | Hypervisor Hostname                                             |
| HYPERVISOR_SERVER_COUNT       | `int`    | "running_vms"                      | The number of running VMs on this hypervisor.                   |
| HYPERVISOR_STATE              | `string` | "state"                            | The state of the hypervisor. One of up or down.                 |
| HYPERVISOR_STATUS             | `string` | "status"                           | The status of the hypervisor. One of enabled or disabled.       |
| HYPERVISOR_VCPUS              | `int`    | "vcpus"                            | The number of vCPUs on this hypervisor.                         |
| HYPERVISOR_VCPUS_USED         | `int`    | "vcpus_used"                       | The number of vCPUs currently being used on this hypervisor.    |
| HYPERVISOR_DISABLED_REASON    | `string` | "disabled_reason"                  | Comment of why the hypervisor is disabled, None if not disabled |


Any of these properties can be used for any of the API methods that takes a property - like `select`, `where`, `sort_by` etc

## Chaining
This section details valid mappings you can use to chain onto other queries or from other queries to chain into a `HypervisorQuery` object.
This applies to API calls `then` and `append_from` - see [API.md](../API.md) for details

## Query Alias
The aliases that can be used for the query when chaining are listed below:

| Query Enum                 | Aliases (case-insensitive    |
|----------------------------|------------------------------|
| QueryTypes.HypervisorQuery | "hypervisor", "hypervisors"  |



## Chaining from
A `HypervisorQuery` can be chained to other queries.
The following shared-common properties are listed below (as well as the Query object they map to):

| Prop 1                             | Prop 2                          | Type        | Maps                                | Documentation            |
|------------------------------------|---------------------------------|-------------|-------------------------------------|--------------------------|
| HypervisorProperties.HYPERVISOR_ID | ServerProperties.HYPERVISOR_ID  | One-to-Many | `HypervisorQuery` to `ServerQuery`  | [SERVERS.md](SERVERS.md) |


## Chaining to
Chaining from other `HypervisorQuery` requires passing `HYPERVISOR_QUERY` or any aliases mentioned above as the `query_type`

| From          | Prop 1                         | Prop 2                             | Type        | Documentation            |
|---------------|--------------------------------|------------------------------------|-------------|--------------------------|
| `ServerQuery` | ServerProperties.HYPERVISOR_ID | HypervisorProperties.HYPERVISOR_ID | Many-to-One | [SERVERS.md](SERVERS.md) |


## run() meta-parameters

`HypervisorQuery()` accepts no extra meta-parameters when calling `run()`
