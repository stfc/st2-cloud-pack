# Flavors
Flavors refer to Openstack Compute Flavors. Flavors define the compute, memory, and storage capacity of nova computing instances.
See [Openstack Docs](https://docs.openstack.org/api-ref/compute/#flavors) for more info

**NOTE: `FlavorQuery` will only work with admin credentials - set by `clouds.yaml`**

## Querying

To Query for Flavors using the Query Library, you can import `FlavorQuery()` like so:

```python
from openstack_query import FlavorQuery
```

`FlavorQuery()` can then be used to setup and run queries - see [API.md](../API.md) for details on API calls

## Properties

The Valid property enum for `FlavorQuery` is `FlavorProperties`. You can import `FlavorProperties` like so:

```python
from enums.query.props.flavor_properties import FlavorProperties
```

`FlavorProperties` exposes the following properties:

| Property Enum      | Type     | Aliases | Description                                                                                     |
|--------------------|----------|---------|-------------------------------------------------------------------------------------------------|
| FLAVOR_DESCRIPTION | `string` | `None`  | The description of the flavor                                                                   |
| FLAVOR_DISK        | `int`    | `None`  | Size of the disk this flavor offers. Type: int                                                  |
| FLAVOR_EPHEMERAL   | `int`    | `None`  | Size of the ephemeral data disk attached to this server. Type: int                              |
| FLAVOR_ID          | `string` | `None`  | Unique ID Openstack has assigned the flavor.                                                    |
| FLAVOR_IS_DISABLED | `bool`   | `None`  | Indicates whether flavor is disabled. <br/>True if disabled, False if not                       |
| FLAVOR_IS_PUBLIC   | `bool`   | `None`  | Indicates if flavor is available to all projects. <br/>True if publicly available, False if not |
| FLAVOR_NAME        | `string` | `None`  | Name of the flavor                                                                              |
| FLAVOR_RAM         | `int`    | `None`  | The amount of RAM (in MB) this flavor offers. Type: int                                         |
| FLAVOR_SWAP        | `int`    | `None`  | Size of the swap partitions.                                                                    |
| FLAVOR_VCPU        | `int`    | `None`  | The number of virtual CPUs this flavor offers. Type: int                                        |

Any of these properties can be used for any of the API methods that takes a property - like `select`, `where`, `sort_by` etc
Alternatively, you can pass property aliases (passed as string) instead (currently WIP)

## Chaining
This section details valid mappings you can use to chain onto other queries or from other queries to chain into a `FlavorQuery` object.
This applies to API calls `then` and `append_from` - see [API.md](../API.md) for details


## Chaining from
A `FlavorQuery` can be chained to other queries.
The following shared-common properties are listed below (as well as the Query object they map to):

| Prop 1                     | Prop 2                     | Type        | Maps                           | Documentation            |
|----------------------------|----------------------------|-------------|--------------------------------|--------------------------|
| FlavorProperties.FlAVOR_ID | ServerProperties.FLAVOR_ID | One-to-Many | `FlavorQuery` to `ServerQuery` | [SERVERS.md](SERVERS.md) |


## Chaining to
Chaining from other `FlavorQuery` requires passing `FLAVOR_QUERY` as the `query_type`

| From          | Prop 1                     | Prop 2                     | Type        | Documentation            |
|---------------|----------------------------|----------------------------|-------------|--------------------------|
| `ServerQuery` | ServerProperties.FLAVOR_ID | FlavorProperties.FLAVOR_ID | Many-to-One | [SERVERS.md](SERVERS.md) |


## run() meta-parameters

`FlavorQuery()` accepts no extra meta-parameters when calling `run()`
