# Query Properties

Properties refer to the different key-word arguments that are stored in the Openstack resource.

Properties for each query are defined by Property Enums
- This is done so that names of each property are less ambiguous.
- Allows us to implement aliases for these properties that are independent of Openstacksdk

For each Query object, there is a corresponding enum class `<Resource>Properties` that is used for storing properties.
- located in `lib/enums/query/props` - usually in file called `<resource>_properties.py`


# Property Class Reference

| Property Class      | Description                                                                      |
|---------------------|----------------------------------------------------------------------------------|
| `ServerProperties`  | Properties related to Openstack Servers (VMs). Used by `ServerQuery` Query class |
| `UserProperties`    | Properties related to Openstack Users. Used by `UserQuery` Query class           |
| `ProjectProperties` | Properties related to Openstack Projects. Used by `ProjectQuery` Query class     |
| `FlavorProperties`  | Properties related to Openstack Flavors. Used by `FlavorQuery` Query class       |


## Property Reference

`ServerProperties`

| Property Enum            | Aliases | Description                                                                                                                                                                                                                                          |
|--------------------------|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FLAVOR_ID                | `None`  | The ID of the Flavor the Server is using                                                                                                                                                                                                             |
| HYPERVISOR_ID            | `None`  | The ID of the Hypervisor the Server is being hosted on                                                                                                                                                                                               |
| IMAGE_ID                 | `None`  | The ID of the Image the Server is using                                                                                                                                                                                                              |
| PROJECT_ID               | `None`  | The ID of the Project the Server is associated with                                                                                                                                                                                                  |
| SERVER_CREATION_DATE     | `None`  | Timestamp of when the server was created.                                                                                                                                                                                                            |
| SERVER_DESCRIPTION       | `None`  | User provided description of the server.                                                                                                                                                                                                             |
| SERVER_ID                | `None`  | Unique ID Openstack has assigned the server.                                                                                                                                                                                                         |
| SERVER_LAST_UPDATED_DATE | `None`  | Timestamp of when this server was last updated.                                                                                                                                                                                                      |
| SERVER_NAME              | `None`  | User provided name for server                                                                                                                                                                                                                        |
| SERVER_STATUS            | `None`  | The state this server is in. Valid values include <br/>ACTIVE, BUILDING, DELETED, ERROR, HARD_REBOOT, PASSWORD, PAUSED, <br/>REBOOT, REBUILD, RESCUED, RESIZED, REVERT_RESIZE, SHUTOFF, SOFT_DELETED, STOPPED, SUSPENDED, UNKNOWN, or VERIFY_RESIZE. |
| USER_ID                  | `None`  | The ID of the User that owns the server                                                                                                                                                                                                              |
| ADDRESSES                | `None`  | Comma-separated list of IP addresses this server can be accessed through                                                                                                                                                                             |

#
`UserProperties`

| Property Enum    | Aliases | Description                               |
|------------------|---------|-------------------------------------------|
| USER_DOMAIN_ID   | `None`  | The ID for the domain which owns the user |
| USER_DESCRIPTION | `None`  | The description of this user.             |
| USER_EMAIL       | `None`  | The email address of this user.           |
| USER_ID          | `None`  | Unique ID Openstack has assigned the user |
| USER_NAME        | `None`  | Unique user name (within the domain)      |


#
`ProjectProperties`


| Property Enum       | Aliases | Description                                                                                                                                                        |
|---------------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PROJECT_DESCRIPTION | `None`  | The description of the project                                                                                                                                     |
| PROJECT_DOMAIN_ID   | `None`  | The ID of the domain which owns the project;                                                                                                                       |
| PROJECT_ID          | `None`  | Unique ID Openstack has assigned the project.                                                                                                                      |
| PROJECT_IS_DOMAIN   | `None`  | Indicates whether the project also acts as a domain. <br/>If set to True, the project acts as both a project and a domain.                                         |
| PROJECT_IS_ENABLED  | `None`  | Indicates whether users can authorize against this project. <br/>if set to False, users cannot access project, additionally all authorized tokens are invalidated. |
| PROJECT_NAME        | `None`  | Name of the project                                                                                                                                                |
| PROJECT_PARENT_ID   | `None`  | The ID of the parent of the project.                                                                                                                               |

#
`FlavorProperties`


| Property Enum      | Aliases | Description                                                                                     |
|--------------------|---------|-------------------------------------------------------------------------------------------------|
| FLAVOR_DESCRIPTION | `None`  | The description of the flavor                                                                   |
| FLAVOR_DISK        | `None`  | Size of the disk this flavor offers. Type: int                                                  |
| FLAVOR_EPHEMERAL   | `None`  | Size of the ephemeral data disk attached to this server. Type: int                              |
| FLAVOR_ID          | `None`  | Unique ID Openstack has assigned the flavor.                                                    |
| FLAVOR_IS_DISABLED | `None`  | Indicates whether flavor is disabled. <br/>True if disabled, False if not                       |
| FLAVOR_IS_PUBLIC   | `None`  | Indicates if flavor is available to all projects. <br/>True if publicly available, False if not |
| FLAVOR_NAME        | `None`  | Name of the flavor                                                                              |
| FLAVOR_RAM         | `None`  | The amount of RAM (in MB) this flavor offers. Type: int                                         |
| FLAVOR_SWAP        | `None`  | Size of the swap partitions.                                                                    |
| FLAVOR_VCPU        | `None`  | The number of virtual CPUs this flavor offers. Type: int                                        |


## Adding a property related to an existing resource

To add or alter a property, locate the enum class holding property mappings for the specific resource you want to change.
(Usually `enums/props/<resource>_properties.py`)

Add a new mapping like so (Adding a new property to `ServerProperties`:

```python

class ServerProperties(PropEnum):
    ...

    FLAVOR_ID = auto()
    ...
    NEW_PROP = auto() # This Adds a new enum value to represent you new property

    ...

     @staticmethod
        def get_prop_mapping(prop):
        ...
        mapping = {
            ...
            # This adds a mapping from enum to a anonymous lambda function which will take an Openstack Server object
            # and get the value for `NEW_PROP`
            ServerProperties.NEW_PROP: lambda a: a["new_prop"]

            # You can also write the function to get the property as a method in the Class
            # and map your enum to that - like we did for ADDRESSES
            ServerProperties.ADDRESSES: ServerProperties.get_ips,
        }
```
