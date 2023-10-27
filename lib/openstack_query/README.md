### Note: This is under active development
### TODO: The Query Library needs to be moved out of StackStorm and into a standalone repo

# Openstack Query Library

A Python Package to query for Openstack Resources.

Built on top of the [openstacksdk](https://docs.openstack.org/openstacksdk/latest/) to allow for more complex queries.

Our overall goal is to provide a better, easier-to-use interface to run openstack queries
The query library will act as a wrapper around the openstacksdk for running queries.

We aim to provide both a python package and a CLI version.

It will address the following issues:

### 1. Improved Error Handling
- The library api will fail-fast and fail-noisily.
- provides clear error messages if the query is invalid.
- mitigate problems with mistyped names/filter options - common with the openstacksdk.


### 2. Improved Reusability
- common query workflows will be integrated into the query
- e.g. finding user names/emails for a server


### 3.  Extend Query Capabilities
- implement query logic missing from openstacksdk. e.g. search by date time
- chain queries together
  - e.g. find servers that are shutoff AND errored THEN find users belonging to them


### 4. Improved Grouping/Sorting Functionality
- allows sorting by multiple keys
- group the results together in different ways
- output only specific properties you want
- write to files, or to different output formats


### 5. Easy to use syntax
- sql-like syntax makes it easy to use

An example of how to use the query library:

Get all VMs on prod cloud domain which are errored or shutoff and output

# Usage


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
# user_ids = user_query.group_by(UserProperties.USER_ID).to_list().keys()
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
#   project_ids = server_query.group_by(ServerProperties.PROJECT_ID).to_list().keys()
#   p = ProjectQuery().select(ProjectProperties.PROJECT_NAME).where(
#        QueryPresetsGeneric.ANY_IN, ProjectProperties.PROJECT_ID, values=list(project_ids)
#   )
#   p.run("prod")
#   res = p.to_list()
# `res` is then combined zipped together into the current output
server_query.append_from("PROJECT_QUERY", "prod", ProjectProperties.PROJECT_ID)

# Note it's not possible to group by external properties (yet)
server_query.group_by(ServerProperties.PROJECT_ID)

# This will print out results and includes project name for every VM too
server_query.to_string()
```

### NOTE - requirement to use enums for properties and query presets will be removed soon - see issue [88](https://github.com/stfc/st2-cloud-pack/issues/88)


# Outputting

you can output the results of your query in the following ways:

`to_list()` - output the info to a list or a dict (if grouped)

**optional params:**

- `as_objects`: `bool`
    - if True will return results as Openstack Objects instead of selected for properties
      - if group_by() was run - then the results will be a dictionary
    - if False will return selected for results as normal


- `flatten`: `bool`

If True will flatten the results by selected for properties:

Instead of returning:
```python
print(query.to_list(flatten=False))

[

  # first result
  { "project_name": "foo", "project_id": "bar" },

  # second result
  { "project_name": "foo1", "project_id": "bar2" },
  ...
]
```

it will return:
```python
print(query.to_list(flatten=True))

{
    "project_name": ["foo", "foo1"],
    "project_id": ["bar", "bar1"]
}
```

If the results are grouped:

Instead of returning:
```python
print(grouped_query.to_list(flatten=False))

{
    "group1": [
        { "project_name": "foo", "project_id": "bar" },
        { "project_name": "foo1", "project_id": "bar2" },
    ],
    "group2": [
        {"project_name": "biz", "project_id": "baz"},
        {"project_name": "biz2", "project_id": "baz2"}
    ]
}
```
It will return:
```python
print(grouped_query.to_list(flatten=True))

{
    "group1": {
        "project_name": ["foo", "foo1"],
        "project_id": ["bar", "bar1"]
    },
    "group2": {
        "project_name": ["biz", "biz1"],
        "project_id": ["baz", "baz1"]
    }
}
```

  - `groups`: List[str] - limit output to only a set of specified group keys


`to_string()` - output results as a tabulate table

- accepts tabulate kwargs - see [tabulate](https://pypi.org/project/tabulate/)
- optional param `groups` works same as `to_list`
- optional param `title` - allows you to set a heading title for the table

`to_html()`- output results as a tabulate html compatible table

- accepts tabulate kwargs - see [tabulate](https://pypi.org/project/tabulate/)
- optional param `title` - allows you to set a html heading title for the table
- optional param `groups` works same as  `to_list`

`to_csv` - in development

`to_json` - in development

other output possibilities coming soon

# Sorting
You can sort the results using `sort_by`

query library allows sorting by multiple keys.
The keys can currently only be supported properties of the query.

`sort_by` takes a number of tuples of property and sort order enum

```python
query = ServerQuery().select(ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME)
query.where(QueryPresetsGeneric.ANY_IN, ServerProperties.SERVER_STATUS, values=["ERROR", "SHUTOFF"])
query.run("prod")

# sort by project_id (ascending), then sort by server_id (descending)
query.sort_by(
    (ServerProperties.PROJECT_ID, SortOrder.ASC),
    (ServerProperties.SERVER_ID, SortOrder.DESC)
)

# sorting will only happen when the output is evaluated.
query.to_string()

# sort by flavor_id (ascending) - overrides previous sort function
query.sort_by(
    (ServerProperties.FLAVOR_ID, SortOrder.ASC)
)

# new sorting config takes effect here
query.to_string()

```



# Grouping

You can group results using `group_by`

Group by partitions results based on a 'group_key'. Like sorting, grouping only works on supported properties of the query

The Query Library currently supports:

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

## Note:  Include Missing
If you are specifying group_keys, you can provide an additional flag `include_missing`

if True: Group by will add an extra group which contains all the values found in results that won't be part of any pre-configured group
