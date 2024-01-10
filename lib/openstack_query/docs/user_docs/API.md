
# Query Library API Reference
Query Library allows complex queries to be run on Openstack resources. It utilises an SQL-like syntax to setup
a query in a declarative way.

This document describes how to use the SQL-like API to run Openstack Queries

## Querying on Resources

The query library currently supports queries on the following Openstack resources

**NOTE**: In development - more query options will be added

| Openstack Resource                                                                                       | Description                            | Reference for Query Object            | How to Import                              |
|----------------------------------------------------------------------------------------------------------|----------------------------------------|---------------------------------------|--------------------------------------------|
| [Servers](https://docs.openstack.org/api-ref/compute/#servers-servers)                                   | Run a Query on Openstack Servers (VMs) | [SERVERS.md](query_docs/SERVERS.md)   | `from openstack_query import ServerQuery`  |
| [Users](https://docs.openstack.org/api-ref/identity/v3/index.html?expanded=list-users-detail#users)      | Run a Query on Openstack Users         | [USERS.md](query_docs/USERS.md)       | `from openstack_query import UserQuery`    |
| [Project](https://docs.openstack.org/api-ref/identity/v3/index.html?expanded=list-users-detail#projects) | Run a Query on Openstack Projects      | [PROJECTS.md](query_docs/PROJECTS.md) | `from openstack_query import ProjectQuery` |
| [Flavor](https://docs.openstack.org/api-ref/compute/#flavors)                                            | Run a Query on Openstack Flavors       | [FLAVORS.md](query_docs/FLAVORS.md)   | `from openstack_query import FlavorQuery`  |

#
### select

`select()` allows you to run a query and output only specific properties from the results.
This is mutually exclusive to returning objects using `select_all()` which will return every available property


```python
def select(*props: Union[str, PropEnum])
```
**Arguments**:

- `props`: one or more properties to collect described as enum or an equivalent string alias.
  - e.g. If you're querying servers with `ServerQuery` - appropriate enum is `ServerProperties`,
  - see the specific query page e.g. [SERVERS.md](query_docs/SERVERS.md) on supported properties and string aliases for that query

Running `select()` again will override all currently selected properties from previous `select()` call

`select()` and `select_all()` calls will be ignored when `to_objects()` is invoked
`select()` is mutually exclusive to `select_all()`

**Examples**

```python
from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties

# create a ServerQuery and find server names and ids
query = ServerQuery()
query.select(ServerProperties.SERVER_NAME, ServerProperties.SERVER_ID)

# or using the equivalent string aliases
query.select("server_name", "server_id")
```

#
### select\_all

`select_all()` will set the query to output all properties stored for the property to be returned .
Mutually exclusive to returning specific properties using select()

```python
def select_all()
```
**Arguments**:
- None

Running `select_all()` will override currently selected properties from previous `select()` calls

`select_all()` will not work if `to_objects` is called - since it returns Openstack objects

#
### where
`where()` allows you to specify conditions for the query.

`where()` requires a preset-property pair to work.
- A preset is a special enum that defines the logic to query by - see [PRESETS.md](PRESETS.md)
- A property is what the preset will be used on
- (optional) A set of key-word arguments that the preset-property pair require - like a value to compare against

This can be called multiple times to define multiple conditions for the query - acts as Logical AND.

```python
def where(preset: Union[str, QueryPresets], prop: Union[str, PropEnum], **kwargs)
```

**Arguments**:

- `preset`: QueryPreset Enum (or equivalent string alias) to use
  - this specifies the logic to refine the query by. See [PRESETS.md](../PRESETS.md).
- `prop`: Property Enum (or equivalent string alias) that the query preset will be used on -
  - e.g. If you're querying servers with `ServerQuery` - appropriate enum is `ServerProperties`
  - some presets can only accept certain props - see [FILTER_MAPPINGS.md](../FILTER_MAPPINGS.md)
- `kwargs`: a set of optional arguments to pass along with the query preset
  - these kwargs are dependent on the preset - see [PRESETS.md](../PRESETS.md)

**Example(s)**

To query for servers which are in "error" state - the values would be:
- preset - `QueryPresetsGeneric.EQUAL_TO`
- prop - `ServerProperties.SERVER_STATUS`
- value(s) - `value="ERROR"`

the `where` call would be like so:
```python
from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enum.query.query_presets import QueryPresetsGeneric

# create a ServerQuery
query = ServerQuery()
query.select_all()

# setup filter server_status = ERROR
query.where(
    preset=QueryPresetsGeneric.EQUAL_TO,
    prop=ServerProperties.SERVER_STATUS,
    value="ERROR"
)

# or using the equivalent string aliases
query.where("EQUAL_TO", "server_status", value="ERROR")
```

#
### sort\_by

`sort_by` allows you to sort results by given property(ies) before outputting.

It allows sorting by multiple keys if you provide multiple `sort_by` tuples.

```python
def sort_by(*sort_by: Tuple[Union[str, PropEnum], Union[str, SortOrder]])
```

**Arguments**:

- `sort_by`: Takes any number of tuples - the tuples must consist of two values:
  - a property enum (or equivalent alias) to sort by
    -  e.g. If you're querying servers with `ServerQuery` - appropriate enum is `ServerProperties`
  - an enum (or equivalent alias) representing the sort order
    - `SortOrder.ASC` (for ascending) or `SortOrder.DESC` (for descending)

| SortOrder Enum | Description              | Alias(es) (case-insensitive) |
|----------------|--------------------------|------------------------------|
| SortOrder.ASC  | sort in ascending order  | "ascending", "asc"           |
| SortOrder.DESC | sort in descending order | "descending", "desc"         |

**Note**: You can sort by properties you haven't 'selected' for using `select()`

**Examples**

```python
from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enum.query.query_presets import QueryPresetsGeneric
from enum.query.sort_order import SortOrder

# create a ServerQuery
query = ServerQuery()
query.select(ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME)
query.run("openstack-domain", as_admin=True, all_projects=True)

# sort by name in descending, then sort by id in ascending
query.sort_by(
  (ServerProperties.SERVER_ID, SortOrder.DESC),
  (ServerProperties.SERVER_NAME, SortOrder.ASC)
)

# or using equivalent string aliases
query.sort_by(
  ("server_id", "descending"),
  ("server_name", "ascending")
)

print(query.to_string())
```

results sorted by server name in descending (alphabetical) order, then if server name is the same,
we sort by server_id in ascending order etc.
```commandline
+--------------------------------------------+--------------------------------------+
| server_name                                | server_id                            |
+==================================================================================+
| foo2                                       | 3                                    |
+--------------------------------------------+--------------------------------------+
| foo                                        | 1                                    |
+--------------------------------------------+--------------------------------------+
| foo                                        | 2                                    |
+--------------------------------------------+--------------------------------------+
| bar                                        | 4                                    |
+--------------------------------------------+--------------------------------------+
```

#
### group\_by

`group_by` allows you to group the results before outputting by either:
- unique values found for a property specified in `group_by`
- a set of pre-defined groups which define how to group results based on their value of the property specified in `group_by`

```python
def group_by(group_by: Union[str, PropEnum],
             group_ranges: Optional[Dict[str, List[PropValue]]] = None,
             include_ungrouped_results: bool = False)
```

Public method used to configure how to group results.

**Arguments**:

- `group_by`: a property enum (or equivalent string alias) representing the property you want to group by
    - e.g. If you're querying servers with `ServerQuery` - appropriate enum is `ServerProperties`
- `group_ranges`: (optional) a dictionary of group mappings
  - the keys are unique group names
  - the values are a list of values that `group_by` property could have to be included in that group
- `include_ungrouped_results`: (optional) flag that if true - will include an "ungrouped" group (Default is `False`)
  - ungrouped group will contain all results that have a `group_by` property value that does not match any of the
  groups set in `group_ranges`

**Note**: You can group by properties you haven't 'selected' for using `select()`

**Examples**
Running an `ANY_IN` command and grouping results

```python

from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enum.query.query_presets import QueryPresetsGeneric

# create a ServerQuery
query = ServerQuery()
query.select(ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME)

# setup filter server_status = ERROR
query.where(
    preset="ANY_IN"
    prop="server_status",
    values=["ERROR", "SHUTOFF"]
)
query.run("openstack-domain", as_admin=True, all_projects=True)
query.group_by("server_status")

# holds a dictionary - where keys are unique values of "server_status" in results
# in this case - ERROR and SHUTOFF since we queried for them
x = query.to_objects()
```

```commandline
> {"ERROR": [
        {"server_id": 1, "server_name": "foo"},
        {"server_id": 2, "server_name": "bar"},
   ],
   "SHUTOFF": [
        {"server_id": 3, "server_name": "biz"},
        {"server_id": 4, "server_name": "baz"},
   ]
```

#
### run

`run()` will run the query. `run()` will apply all predefined conditioned set by `where` calls

```python
def run(cloud_account: Union[str, CloudDomains],
        from_subset: Optional[List[OpenstackResourceObj]] = None,
        **kwargs)
```

**Arguments**:

- `cloud_account`: A String or a CloudDomains Enum representing the clouds configuration to use
  - this should be the domain set in the `clouds.yaml` file located in `.config/openstack/clouds.yaml`

- `from_subset`: (optional) a subset of openstack resources to run query on instead of querying for them using openstacksdk
  - **NOTE:** this is going to be deprecated soon - look at using `then()` or `append_from()` for a better way to
  chain the result of one query onto another

- `kwargs`: keyword args that can be used to configure details of how query is run
  - see specific documentation for resource for valid keyword args you can pass to `run()`

#
### to\_objects

`to_objects` is an output method that will return results as openstack objects.

Like all output methods - it will parse the results set in `sort_by()`, `group_by()` and requires `run()` to have been called first
- this method will not run `select` - instead outputting raw results (openstack resource objects)

```python
def to_objects(
        groups: Optional[List[str]] = None) -> Union[Dict[str, List], List]
```

This is either returned as a list if `to_groups` has not been set, or as a dict if `to_groups` was set

**Arguments**:

- `groups`: a list of group keys to limit output by - this will only work if `to_groups()` has been set - else it produces an error

**Examples**

```python

from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enum.query.query_presets import QueryPresetsGeneric

# create a ServerQuery
query = ServerQuery()
query.select("server_id", "server_name")

# setup filter server_status = ERROR
query.where(
    preset="EQUAL_TO",
    prop="server_status",
    value="ERROR"
)
query.run("openstack-domain", as_admin=True, all_projects=True)
x = query.to_objects()
```

`x` holds the following: A list of openstack Server objects
```commandline
> [openstack.compute.v2.server.Server(...), openstack.compute.v2.server.Server(...), ...]
```

#
### to\_props
`to_props` is an output method that will return results as a dictionary of selected properties.

Like all output methods - it will parse the results set in `sort_by()`, `group_by()` and requires `run()` to have been called first
- This method will parse results to get properties that we 'selected' for - from a `select()` or a `select_all()` call
- If this query is chained from previous query(ies) by `then()` - the previous results will also be included
- If any `append_from` calls have been run - the properties appended will also be included

```python
def to_props(
        flatten: bool = False,
        groups: Optional[List[str]] = None) -> Union[Dict[str, List], List]
```
This is either returned as a list if `to_groups` has not been set, or as a dict if `to_groups` was set

**Arguments**:

- `flatten`: (optional) boolean flag which will flatten results if true (default is `False`)

If True will flatten the results by selected for properties:

Instead of returning:
```python
print(query.to_props(flatten=False))

[

  # first result
  { "project_name": "foo", "project_id": "bar" },

  # second result
  { "project_name": "foo1", "project_id": "bar1" },
  ...
]
```

it will return:
```python
print(query.to_props(flatten=True))

{
    "project_name": ["foo", "foo1"],
    "project_id": ["bar", "bar1"]
}
```

If the results are grouped:

Instead of returning:
```python
print(grouped_query.to_props(flatten=False))

{
    "group1": [
        { "project_name": "foo", "project_id": "bar" },
        { "project_name": "foo1", "project_id": "bar1" },
    ],
    "group2": [
        {"project_name": "biz", "project_id": "baz"},
        {"project_name": "biz1", "project_id": "baz1"}
    ]
}
```
It will return:
```python
print(grouped_query.to_props(flatten=True))

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

- `groups`: (optional) a list of group keys to limit output by - this will only work if `to_groups()` has been set - else it produces an error

**Examples**

```python

from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enum.query.query_presets import QueryPresetsGeneric

# create a ServerQuery
query = ServerQuery()
query.select(ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME)
query.run("openstack-domain", as_admin=True, all_projects=True)
# setup filter server_status = ERROR
query.where(
    preset=QueryPresetsGeneric.EQUAL_TO,
    prop=ServerProperties.SERVER_STATUS,
    value="ERROR"
)

x = query.to_props()
# x would hold a list of dictionaries that contain only the info you've selected
```
```commandline
> [{"server_id": 1, "server_name": "foo"}, {"server_id": 2, "server_name": "bar"}, ...]
```

if `flatten=True`
```python
  x = query.to_props(flatten=True)
  # x would hold a list of dictionaries that contain only the info you've selected
```
```commandline
> {"server_name": ["foo", "bar", ...], "server_id": [1, 2, ...]}
```

#
### to\_string
`to_string` is an output method that will return results as a tabulate table(s) (in string format).

Like all output methods - it will parse the results set in `sort_by()`, `group_by()` and requires `run()` to have been called first
- This method will parse results to get properties that we 'selected' for - from a `select()` or a `select_all()` call
- If this query is chained from previous query(ies) by `then()` - the previous results will also be included
- If any `append_from` calls have been run - the properties appended will also be included

```python
def to_string(title: Optional[str] = None,
              groups: Optional[List[str]] = None,
              **kwargs) -> str
```

**Arguments**:

- `title`: An optional title to print on top
- `groups`: a list of group keys to limit output by - this will only work if `to_groups()` has been set - else it produces an error
- `include_group_titles`: A boolean (Default True), if True, will print the group key as a subtitle before printing each selected group table, if False no subtitle will be printed.
- `kwargs`: kwargs to pass to tabulate to tweak table generation
  - see [tabulate](https://pypi.org/project/tabulate/) for valid kwargs
  - note `to_string` calls tabulate with `tablefmt="plaintext"`

**Examples**

```python

from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enum.query.query_presets import QueryPresetsGeneric

# create a ServerQuery
query = ServerQuery()
query.select(ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME)

# setup filter server_status = ERROR
query.where(
    preset=QueryPresetsGeneric.EQUAL_TO,
    prop=ServerProperties.SERVER_STATUS,
    value="ERROR"
)
query.run("openstack-domain", as_admin=True, all_projects=True)

print(query.to_string())

```
```commandline
+--------------------------------------------+--------------------------------------+
| server_name                                | server_id                            |
+==================================================================================+
| foo                                        | 1                                    |
+--------------------------------------------+--------------------------------------+
| bar                                        | 2                                    |
+--------------------------------------------+--------------------------------------+
```

#
### to\_html
`to_html` is an output method that will return results as a tabulate table(s) (in string format - in html format).

Like all output methods - it will parse the results set in `sort_by()`, `group_by()` and requires `run()` to have been called first
- This method will parse results to get properties that we 'selected' for - from a `select()` or a `select_all()` call
- If this query is chained from previous query(ies) by `then()` - the previous results will also be included
- If any `append_from` calls have been run - the properties appended will also be included

```python
def to_html(title: Optional[str] = None,
              groups: Optional[List[str]] = None,
              **kwargs) -> str
```

**Arguments**:

- `title`: An optional title to print on top
- `groups`: a list of group keys to limit output by - this will only work if `to_groups()` has been set - else it produces an error
- `include_group_titles`: A boolean (Default True), if True, will print the group key as a subtitle before printing each selected group table, if False no subtitle will be printed.
- `kwargs`: kwargs to pass to tabulate to tweak table generation
  - see [tabulate](https://pypi.org/project/tabulate/) for valid kwargs
  - note `to_html` calls tabulate with `tablefmt="html"`


**Examples**

```python

from openstack_query import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enum.query.query_presets import QueryPresetsGeneric

# create a ServerQuery
query = ServerQuery()
query.select(ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME)

# setup filter server_status = ERROR
query.where(
    preset=QueryPresetsGeneric.EQUAL_TO,
    prop=ServerProperties.SERVER_STATUS,
    value="ERROR"
)
query.run("openstack-domain", as_admin=True, all_projects=True)

print(query.to_html())

```
```commandline
<table>
<thead>
<tr><th>server_id                     </th><th>server_name                               </th></tr>
</thead>
<tbody>
<tr><td>1                             </td><td>foo                                       </td></tr>
<tr><td>2                             </td><td>bar                                       </td></tr>

```

#
### to_csv (Under development)
`to_csv` is an output method that will write the output into csv file(s). If the results are grouped, each group will be written to a file under `<unique-group-key>.csv`

Like all output methods - it will parse the results set in `sort_by()`, `group_by()` and requires `run()` to have been called first
- This method will parse results to get properties that we 'selected' for - from a `select()` or a `select_all()` call
- If this query is chained from previous query(ies) by `then()` - the previous results will also be included
- If any `append_from` calls have been run - the properties appended will also be included

```python
def to_csv(dirpath: str)
```

**Arguments**:

**NOTE:** More args for to_csv method under development

- `dirpath`: path to directory where file(s) will be written, can be a filepath, but will error if results are grouped

#
### to_json (Under development)

#
### then
`then()` chains current query onto another query of a different type.
It takes the results of the current query and uses them to run another query

This can only work if the current query and the next query have a shared common property

- Query must be run first by calling `run()` before calling `then()`
- A shared common property must exist between this query and the new query
   - i.e. both ServerQuery and UserQuery share the 'USER_ID' property so chaining is possible between them


**NOTE:** Any parsing calls - i.e. `group_by` or `sort_by` will be ignored

**NOTE:** You will NOT be able to group/sort by forwarded properties in the new query

```python
def then(query_type: Union[str, QueryTypes],
         keep_previous_results: bool = True)
```

**Arguments**:

- `query_type`: an enum (or equivalent string alias) representing the new query to chain into
  - see specific documentation for resource for valid ways `query_types`

- `keep_previous_results`: flag that:
  - If True - will forward outputs from this query (and previous chained queries) onto new query.
  - If False - runs the query based on the previous results as a filter without adding additional fields

**Examples:**
See [USAGE.md](USAGE.md) for complex query examples where you would use `then()`

#
### append\_from
`append_from()` appends specific properties from other queries to the output.

This method will run a secondary query on top of this one to get required properties and append each result to the results of this query

- Query must be run first by calling `run()` before calling `append_from()`
- A shared common property must exist between this query and the new query
   - i.e. both ServerQuery and UserQuery share the 'USER_ID' property so `append_from` is possible between them
   - see specific documentation for resource for valid ways to chain

**NOTE:** You will NOT be able to group/sort by forwarded properties in the new query

```python
def append_from(query_type: Union[str, QueryTypes],
                cloud_account: Union[str, CloudDomains], *props: Union[str, PropEnum])
```

**Arguments**:

- `query_type`: an enum (or equivalent string alias) representing the new query to chain into
  - see specific documentation for resource for valid ways `query_types`

- `cloud_account`: A CloudDomains Enum (or equivalent string alias) for the clouds configuration to use
  - this should be the domain set in the `clouds.yaml` file located in `.config/openstack/clouds.yaml`
- `props`: one or more properties to collect described as enum (or equivalent string alias) from new query.
  - e.g. If you're appending server properties (i.e. `append_from("ServerQuery" ...)`) the appropriate enum is `ServerProperties`
  - see specific documentation for resource you want to append props from to see valid props


**Examples:**
See [USAGE.md](USAGE.md) for complex query examples where you would use `append_from()`
