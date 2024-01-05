# Users
Users refer to Openstack Users. A User in Openstack is an individual who has access to the Openstack API and is owned
by a domain.
See [Openstack Docs](https://docs.openstack.org/api-ref/identity/v3/index.html#users) for more info

**NOTE: `UserQuery` will only work with admin credentials - set by `clouds.yaml`**

## Querying

To Query for Users using the Query Library, you can import `UserQuery()` like so:

```python
from openstack_query import UserQuery
```

`UserQuery()` can then be used to setup and run queries - see [API.md](../API.md) for details on API calls

## Properties

The Valid property enum for `UserQuery` is `UserProperties`. You can import `UserProperties` like so:

```python
from enums.query.props.user_properties import UserProperties
```

`UserProperties` exposes the following properties:

| Property Enum    | Type     | Aliases                                                      | Description                               |
|------------------|----------|--------------------------------------------------------------|-------------------------------------------|
| USER_DOMAIN_ID   | `string` | "domain_id"                                                  | The ID for the domain which owns the user |
| USER_DESCRIPTION | `string` | "description", "desc"                                        | The description of this user.             |
| USER_EMAIL       | `string` | "email", "email_addr", "email_address", "user_email_address" | The email address of this user.           |
| USER_ID          | `string` | "id", "uuid"                                                 | Unique ID Openstack has assigned the user |
| USER_NAME        | `string` | "name", "username                                            | Unique user name (within the domain)      |


Any of these properties can be used for any of the API methods that takes a property - like `select`, `where`, `sort_by` etc
Alternatively, you can pass property aliases (passed as string) instead (currently WIP)

## Chaining
This section details valid mappings you can use to chain onto other queries or from other queries to chain into a `ProjectQuery` object.
This applies to API calls `then` and `append_from` - see [API.md](../API.md) for details


## Query Alias
The aliases that can be used for the query when chaining are listed below:

| Query Enum            | Aliases (case-insensitive |
|-----------------------|---------------------------|
| QueryTypes.USER_QUERY | "user", "users"           |



## Chaining from
A `UserQuery` can be chained to other queries.
The following shared-common properties are listed below (as well as the Query object they map to):

| Prop 1                 | Prop 2                   | Type        | Maps                         |
|------------------------|--------------------------|-------------|------------------------------|
| UserProperties.USER_ID | ServerProperties.USER_ID | One-to-Many | `UserQuery` to `ServerQuery` |


## Chaining to
Chaining from other `UserQuery` requires passing `USER_QUERY` or any aliases mentioned above as the `query_type`

| From          | Prop 1                   | Prop 2                 | Type        | Documentation            |
|---------------|--------------------------|------------------------|-------------|--------------------------|
| `ServerQuery` | ServerProperties.USER_ID | UserProperties.USER_ID | Many-to-One | [SERVERS.md](SERVERS.md) |


## run() meta-parameters

`UserQuery()` has the following meta-parameters that can be used when calling `run()` to fine-tune the query.

| Parameter Definition                                             | Optional? | Description                                                                                                                                                                                                                                  |
|------------------------------------------------------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `from_domain: UserDomains` <br/><br/>(see `/enums/user_domains`) | Yes       | A User Domain to limit User query to<br/>Optional, if not given will run search on DEFAULT_DOMAIN - `UserDomains.STFC` <br/><br /> NOTE: it is possible to specify user domain via `where()` - if both are provided then an error is raised) |
