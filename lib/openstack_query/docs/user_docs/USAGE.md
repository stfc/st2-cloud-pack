# Usage
The following document contains different ways to use the query library

## Simple Query
Find Errored and Shutoff VMs

```python
from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enums.query.query_presets import QueryPresetsGeneric

# Create a Query Object that will search for Openstack VMs
query = ServerQuery()

# Select - when outputting - only output the selected properties from each VM
query.select(ServerProperties.SERVER_NAME, ServerProperties.SERVER_ID)

# Where - define a preset (ANY_IN), a property to apply it to (server_status) and value/s to look for (ERROR, SHUTOFF)
query.where(QueryPresetsGeneric.ANY_IN, ServerProperties.SERVER_STATUS, values=["ERROR", "SHUTOFF"])

# Run - this will run the query in the "prod" cloud domain and with meta-params as_admin and all_projects.
# This will run the query as an admin and will find VMs on every available project
query.run("prod", as_admin=True, all_projects=True)

# Group By - This will group the results by a property - project_id
# NOTE: group by property and selected property are completely independent
query.group_by(ServerProperties.PROJECT_ID)

# Output the query results to table(s) (stored as a string)
print(query.to_string())
```


## Using more than one where()

Find Errored and Shutoff VMs
- AND haven't been updated in 60 days

```python
from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enums.query.query_presets import QueryPresetsGeneric, QueryPresetsDateTime


query = ServerQuery()
query.select(ServerProperties.SERVER_NAME, ServerProperties.SERVER_ID)
query.where(QueryPresetsGeneric.ANY_IN, ServerProperties.SERVER_STATUS, values=["ERROR", "SHUTOFF"])

# ADDITIONAL WHERE - ACTS AS LOGICAL AND
# Extra query preset refines search to look for errored and shutoff VMs that haven't been updated in 60 days
query.where(QueryPresetsDateTime.OLDER_THAN, ServerProperties.SERVER_LAST_UPDATED_DATE, days=60)


query.run("prod", as_admin=True, all_projects=True)
query.group_by(ServerProperties.PROJECT_ID)
print(query.to_string())
```

## Chaining with then()

Find Errored and Shutoff VMs
- AND haven't been updated in 60 days
- AND the user who made the VM must belong to a specific user domain


```python
from openstack_query import UserQuery
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import QueryPresetsGeneric, QueryPresetsDateTime


# setup and run a User Query to get user info for all users in a specific domain
user_query = UserQuery()
user_query.select(UserProperties.USER_NAME, UserProperties.USER_EMAIL)
user_query.where(QueryPresetsGeneric.EQUAL_TO, UserProperties.USER_DOMAIN_ID, value="user-domain-id1")
user_query.run("prod")

# We're going to create a Server Query using the results from the first query

# This is the same as doing:
# user_ids = user_query.group_by(UserProperties.USER_ID).to_props().keys()
# ServerQuery().where(QueryPresetsGeneric.ANY_IN, ServerProperties.USER_ID, values=list(user_ids))

# NOTE: setting keep_previous_results=True will carry over properties we've selected for from the previous query
server_query = user_query.then("SERVER_QUERY", keep_previous_results=True)

# Then we continue as normal!
server_query.select(ServerProperties.SERVER_NAME, ServerProperties.SERVER_ID)
server_query.where(QueryPresetsGeneric.ANY_IN, ServerProperties.SERVER_STATUS, values=["ERROR", "SHUTOFF"])
server_query.where(QueryPresetsDateTime.OLDER_THAN, ServerProperties.SERVER_LAST_UPDATED_DATE, days=60)
server_query.run("prod", as_admin=True, all_projects=True)
server_query.group_by(ServerProperties.PROJECT_ID)

# These results will contain VM associated values for user_name and user_email
# results will only contain VMs belonging to users in "user-domain-id1"
print(server_query.to_string())
```

## Selecting external props using append_from()

Find Errored and Shutoff VMs
- AND haven't been updated in 60 days
- AND the user who made the VM must belong to a specific user domain.
- AND include the PROJECT_NAME

```python
from openstack_query import UserQuery
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from enums.query.props.project_properties import ProjectProperties
from enums.query.query_presets import QueryPresetsGeneric, QueryPresetsDateTime


# setup and run a User Query to get user info for all users in a specific domain
user_query = UserQuery()
user_query.select(UserProperties.USER_NAME, UserProperties.USER_EMAIL)
user_query.where(QueryPresetsGeneric.EQUAL_TO, UserProperties.USER_DOMAIN_ID, value="user-domain-id1")
user_query.run("prod")

server_query = user_query.then("SERVER_QUERY", keep_previous_results=True)
server_query.select(ServerProperties.SERVER_NAME, ServerProperties.SERVER_ID)
server_query.where(QueryPresetsGeneric.ANY_IN, ServerProperties.SERVER_STATUS, values=["ERROR", "SHUTOFF"])
server_query.where(QueryPresetsDateTime.OLDER_THAN, ServerProperties.SERVER_LAST_UPDATED_DATE, days=60)
server_query.run("prod", as_admin=True, all_projects=True)

# We need to get project name by running append_from()
# append_from() command below is the same as doing the following:
#   project_ids = server_query.group_by(ServerProperties.PROJECT_ID).to_props().keys()
#   p = ProjectQuery().select(ProjectProperties.PROJECT_NAME).where(
#        QueryPresetsGeneric.ANY_IN, ProjectProperties.PROJECT_ID, values=list(project_ids)
#   )
#   p.run("prod")
#   res = p.to_props()
# `res` is then combined zipped together into the current output
server_query.append_from("PROJECT_QUERY", "prod", [ProjectProperties.PROJECT_ID])

# Note it's not possible to group by external properties (yet)
server_query.group_by(ServerProperties.PROJECT_ID)

# This will print out results and includes project name for every VM too
server_query.to_string()
```
### NOTE - requirement to use enums for properties and query presets will be removed soon - see issue [88](https://github.com/stfc/st2-cloud-pack/issues/88)

# Grouping Usage

## Group By Unique Values
By default - the unique values of a given property found in results as the 'group_key'
```python

query = ServerQuery().select(ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME)
query.where(QueryPresetsGeneric.ANY_IN, ServerProperties.SERVER_STATUS, values=["ERROR", "SHUTOFF"])
query.run("prod")

# groups by unique values of server_status found in results
#   - in this case we'll get 2 groups - 'ERROR' and 'SHUTOFF' are the group keys
query.group_by(ServerProperties.SERVER_STATUS)
```

## Group By Given Group Keys
You can specify you're own group_keys by setting the values that belong to each group like so:
```python

query = ServerQuery().select(ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME)
query.where(QueryPresetsGeneric.ANY_IN, ServerProperties.SERVER_STATUS, values=["ERROR", "SHUTOFF"])
query.run("prod")

# groups by pre-configured groups
group_keys = {
    # first group must have VMs belonging to project-id1 and project-id2
    "group1": ["project-id1", "project-id2"],
    # second group must have VMs belonging to project-id3 and project-id3
    "group2": ["project-id3", "project-id4"]
}
# groups by pre-configured group keys
#   - in this case we'll get 2 groups - group1 and group2
#   - group1 will contain VMs belonging to project with ids project-id1 and project-id2
#   - group2 will contain VMs belonging to project with ids project-id3 and project-id4
#   - all other VMs will be ignored
query.group_by(ServerProperties.PROJECT_ID, group_keys=group_keys)
```

### Note About Aliases

All these examples use Enums as inputs to various API methods.

Any API methods that take Enums as input can also accept strings that are known as string aliases.
These aliases will be converted to a specific Enum implicitly.

The point of aliases is to be intuitive, and won't require you to learn the specific syntax of the query library.
To see which aliases are available:

1. For Preset aliases for use with `where()` see [Presets.md](PRESETS.md)
2. For Property aliases for use with `select()`, `where()` and others, see the specific page in [query_docs](query_docs)
3. For Query aliases for use with `then()`, append_from()`, see the specific page in [query_docs](query_docs)
4. For other aliases, see API method reference in [API.md](API.md)

**NOTE**: passing a string alias that exactly matches the enum will always be accepted. E.g:

```python
query.select(ServerProperties.SERVER_ID)

# is equivalent to
query.select("server_id")

# both are equivalent to using aliases like:
query.select("id")
# or
query.select("uuid")
```
