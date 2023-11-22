
# Query Library API Reference
Query Library allows complex queries to be run on Openstack resources. It utilises an SQL-like syntax to setup
a query in a declarative way.

This document describes how to use the SQL-like API to run Openstack Queries

## Querying on Resources

The query library currently supports queries on the following Openstack resources

**NOTE**: In development - more query options will be added

| Openstack Resource                                                                                       | Description                            | Query Name     | How to Import                              |
|----------------------------------------------------------------------------------------------------------|----------------------------------------|----------------|--------------------------------------------|
| [Servers](https://docs.openstack.org/api-ref/compute/#servers-servers)                                   | Run a Query on Openstack Servers (VMs) | ServerQuery()  | `from openstack_query import ServerQuery`  |
| [Users](https://docs.openstack.org/api-ref/identity/v3/index.html?expanded=list-users-detail#users)      | Run a Query on Openstack Users         | UserQuery()    | `from openstack_query import UserQuery`    |
| [Project](https://docs.openstack.org/api-ref/identity/v3/index.html?expanded=list-users-detail#projects) | Run a Query on Openstack Projects      | ProjectQuery() | `from openstack_query import ProjectQuery` |
| [Flavor](https://docs.openstack.org/api-ref/compute/#flavors)                                            | Run a Query on Openstack Flavors       | FlavorQuery()  | `from openstack_query import FlavorQuery`  |

### select

`select()` allows you to run a query and output only specific properties from the results.
This is mutually exclusive to returning objects using `select_all()`

```python
def select(*props: PropEnum)
```
**Arguments**:

- `props`: one or more properties to collect described as enum.
  - e.g. If you're querying servers with `ServerQuery` - appropriate enum is `ServerProperties`

Running `select()` again will override all currently selected properties from previous `select()` call

`select()` will not work if `to_objects` is called - since it returns Openstack objects

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
- A preset is a special enum that defines the logic to query by
- A property is what the preset will be used on
- (optional) A set of key-word arguments that the preset-property pair require - like a value to compare against

This can be called multiple times to define multiple conditions for the query - acts as Logical AND.

```python
def where(preset: QueryPresets, prop: PropEnum, **kwargs)
```

**Arguments**:

- `preset`: QueryPreset Enum to use - this is a special enum that specifies the logic to refine the query by. see PRESETS.md.
- `prop`: Property Enum that the query preset will be used on -
  - e.g. If you're querying servers with `ServerQuery` - appropriate enum is `ServerProperties`
  - some presets only accept certain props - see QUERY_MAPPINGS.md
- `kwargs`: a set of optional arguments to pass along with the query preset
  - these kwargs are dependent on the preset - see PRESETS.md

**Example(s)**

To query for servers which are in "error" state - the values would be:
- preset - `QueryPresetsGeneric.EQUAL_TO`
- prop - `ServerProperties.SERVER_STATUS`
- value(s) - `value="ERROR"`

the `where` call would be like so:
```python
where(
    preset=QueryPresetsGeneric.EQUAL_TO,
    prop=ServerProperties.SERVER_STATUS,
    value="ERROR"
)
```

#
### sort\_by

`sort_by` allows you to sort results by given property(ies) before outputting.

It allows sorting by multiple keys if you provide multiple `sort_by` tuples.

```python
def sort_by(*sort_by: Tuple[PropEnum, SortOrder])
```

**Arguments**:

- `sort_by`: Takes any number of tuples - the tuples must consist of two values:
  - a property enum to sort by
    -  e.g. If you're querying servers with `ServerQuery` - appropriate enum is `ServerProperties`
  - an enum representing the sort order
    - `SortOrder.ASC` (for ascending) or `SortOrder.DESC` (for descending)

**Note**: You can sort by properties you haven't 'selected' for using `select()`


#
### group\_by

`group_by` allows you to group the results before outputting by either:
- unique values found for a property specified in `group_by`
- a set of pre-defined groups which define how to group results based on their value of the property specified in `group_by`

```python
def group_by(group_by: PropEnum,
             group_ranges: Optional[Dict[str, List[PropValue]]] = None,
             include_ungrouped_results: bool = False)
```

Public method used to configure how to group results.

**Arguments**:

- `group_by`: a property enum representing the property you want to group by
    - e.g. If you're querying servers with `ServerQuery` - appropriate enum is `ServerProperties`

- `group_ranges`: (optional) a dictionary of group mappings
  - the keys are unique group names
  - the values are a list of values that `group_by` property could have to be included in that group
- `include_ungrouped_results`: (optional) flag that if true - will include an "ungrouped" group (Default is `False`)
  - ungrouped group will contain all results that have a `group_by` property value that does not match any of the
  groups set in `group_ranges`

**Note**: You can group by properties you haven't 'selected' for using `select()`

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

- `kwargs`: keyword args that can be used to configure details of how query is run
  - see QUERY_MAPPINGS.md for valid keyword args for each Query

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

- `flatten`: (optional) boolean flag which will flatten results if true - see README.md for examples (default is `False`)
- `groups`: a list of group keys to limit output by - this will only work if `to_groups()` has been set - else it produces an error

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
- `kwargs`: kwargs to pass to tabulate to tweak table generation
  - see [tabulate](https://pypi.org/project/tabulate/) for valid kwargs
  - note `to_string` calls tabulate with `tablefmt="plaintext"`

#
### to\_html
`to_html` is an output method that will return results as a tabulate table(s) (in string format - in html format).

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
- `kwargs`: kwargs to pass to tabulate to tweak table generation
  - see [tabulate](https://pypi.org/project/tabulate/) for valid kwargs
  - note `to_html` calls tabulate with `tablefmt="html"`

```python
def to_html(title: Optional[str] = None,
            groups: Optional[List[str]] = None,
            **kwargs) -> str
```

Public method to return results as html table

**Arguments**:

- `title`: an optional title for the table(s) - will be converted to html automatically
- `groups`: a list group to limit output by
- `kwargs`: kwargs to pass to generate table

#
### then
`then()` chains current query onto another query of a different type.
It takes the results of the current query and uses them to run another query - see README.md for more details

This can only work if the current query and the next query have a shared common property - see MAPPINGS.md for more details

- Query must be run first by calling `run()` before calling `then()`
- A shared common property must exist between this query and the new query
   - i.e. both ServerQuery and UserQuery share the 'USER_ID' property so chaining is possible between them
   - see CHAINING.md for more on chaining

**NOTE:** Any parsing calls - i.e. `group_by` or `sort_by` will be ignored

**NOTE:** You will NOT be able to group/sort by forwarded properties in the new query

```python
def then(query_type: Union[str, QueryTypes],
         keep_previous_results: bool = True)
```

**Arguments**:

- `query_type`: an enum representing the new query to chain into - See MAPPINGS.md
- `keep_previous_results`: flag that:
  - If True - will forward outputs from this query (and previous chained queries) onto new query.
  - If False - runs the query based on the previous results as a filter without adding additional fields

**Examples:**
See README.md for examples

#
### append\_from
`append_from()` appends specific properties from other queries to the output.

This method will run a secondary query on top of this one to get required properties and append each result to the results of this query

- Query must be run first by calling `run()` before calling `append_from()`
- A shared common property must exist between this query and the new query
   - i.e. both ServerQuery and UserQuery share the 'USER_ID' property so `append_from` is possible between them
   - see CHAINING.md for more on chaining

**NOTE:** You will NOT be able to group/sort by forwarded properties in the new query

```python
def append_from(query_type: Union[str, QueryTypes],
                cloud_account: Union[str, CloudDomains], *props: PropEnum)
```

**Arguments**:

- `query_type`: an enum representing the new query to chain into - See MAPPINGS.md
- `cloud_account`: A String or a CloudDomains Enum for the clouds configuration to use
  - this should be the domain set in the `clouds.yaml` file located in `.config/openstack/clouds.yaml`
- `props`: one or more properties to collect described as enum from new query.
  - e.g. If you're appending server properties (i.e. `append_from("ServerQuery" ...)`) the appropriate enum is `ServerProperties`


**Examples:**
see README.md for examples
