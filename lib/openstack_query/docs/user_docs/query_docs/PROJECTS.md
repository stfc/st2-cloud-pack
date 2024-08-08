# Projects
Projects refer to Openstack Projects. Projects are organizational units in the cloud to which you can assign users
See [Openstack Docs](https://docs.openstack.org/api-ref/identity/v3/index.html#projects) for more info

**NOTE: `ProjectQuery` will only work with admin credentials - set by `clouds.yaml`**

## Querying

To Query for Projects using the Query Library, you can import `ProjectQuery()` like so:

```python
from openstack_query import ProjectQuery
```

`ProjectQuery()` can then be used to setup and run queries - see [API.md](../API.md) for details on API calls

## Properties

The Valid property enum for `ProjectQuery` is `ProjectProperties`. You can import `ProjectProperties` like so:

```python
from enums.query.props.project_properties import ProjectProperties
```

`ProjectProperties` exposes the following properties:


| Property Enum       | Type     | Aliases               | Description                                                                                                                                                        |
|---------------------|----------|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PROJECT_DESCRIPTION | `string` | "description", "desc" | The description of the project.                                                                                                                                    |
| PROJECT_DOMAIN_ID   | `string` | "domain_id"           | The ID of the domain which owns the project.                                                                                                                       |
| PROJECT_ID          | `string` | "project_id"          | Unique ID Openstack has assigned the project.                                                                                                                      |
| PROJECT_IS_DOMAIN   | `bool`   | "is_domain"           | Indicates whether the project also acts as a domain. <br/>If set to True, the project acts as both a project and a domain.                                         |
| PROJECT_IS_ENABLED  | `bool`   | "is_enabled"          | Indicates whether users can authorize against this project. <br/>if set to False, users cannot access project, additionally all authorized tokens are invalidated. |
| PROJECT_NAME        | `string` | "name"                | Name of the project.                                                                                                                                               |
| PROJECT_PARENT_ID   | `string` | "parent_id"           | The ID of the parent of the project.                                                                                                                               |

Any of these properties can be used for any of the API methods that takes a property - like `select`, `where`, `sort_by` etc
Alternatively, you can pass property aliases (passed as string) instead (currently WIP)

## Chaining
This section details valid mappings you can use to chain onto other queries or from other queries to chain into a `ProjectQuery` object.
This applies to API calls `then` and `append_from` - see [API.md](../API.md) for details

## Query Alias
The aliases that can be used for the query when chaining are listed below:

| Query Enum               | Aliases (case-insensitive |
|--------------------------|---------------------------|
| QueryTypes.PROJECT_QUERY | "project", "projects"     |



## Chaining from
A `ProjectQuery` can be chained to other queries.
The following shared-common properties are listed below (as well as the Query object they map to):


| Prop 1                       | Prop 2                      | Type        | Maps                            |
|------------------------------|-----------------------------|-------------|---------------------------------|
| ProjectProperties.PROJECT_ID | ServerProperties.PROJECT_ID | One-to-Many | `ProjectQuery` to `ServerQuery` |


## Chaining to
Chaining from other `ProjectQuery` requires passing `PROJECT_QUERY` or any aliases mentioned above as the `query_type`

| From          | Prop 1                      | Prop 2                       | Type        | Documentation            |
|---------------|-----------------------------|------------------------------|-------------|--------------------------|
| `ServerQuery` | ServerProperties.PROJECT_ID | ProjectProperties.PROJECT_ID | Many-to-One | [SERVERS.md](SERVERS.md) |


## run() meta-parameters

`ProjectQuery()` accepts no extra meta-parameters when calling `run()`.
