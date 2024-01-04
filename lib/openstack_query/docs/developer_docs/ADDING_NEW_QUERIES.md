# Adding a new Query
The most common new feature for the Query Library would be adding the ability to query a new Openstack resource.
You can do so by doing the following

## 1. Create a PropEnum Class
A new subclass of the `PropEnum` class is required to store valid property enums and mappings for your new openstack
resource. To do this, you must:
1. Identify all available properties for the new query.
   - You can find this information by looking in the openstacksdk api documentation [here](https://docs.openstack.org/openstacksdk/latest/user/index.html#api-documentation).
2. Create a new file under `/enums/query/props/` called `<resource>_properties.py`, replace `<resource>` with the name of the openstack resource you want to query
3. Create the `<resource>Properties` class definition
   - class must inherit from `PropEnum` abstract base class and implement abstract methods.

```python
class ResourceProperties(PropEnum):

    # add enums for each property you found here like so
    PROP_1 = auto() # replace `PROP_1` with property name
    ...

    @staticmethod
    def get_prop_mapping(prop):
        ...
        # add prop mappings here.
        mapping = {
           ResourceProperties.PROP_1: lambda a: a["prop_1"]
        }
        try:
           return mapping[prop]
        except KeyError as exp:
            raise QueryPropertyMappingError(
                f"Error: failed to get property mapping, property {prop.name} is not supported in FlavorProperties"
            ) from exp

    @staticmethod
    def get_marker_prop_func():
        ...
        # marker prop func returns the mapped function for the property that can be used as the marker
        # for pagination
        # here you need to replace ResourceProperties.PROP_1 with the appropriate property enum that can be used as the
        # marker for pagination - this is usually the ID property
        return ResourceProperties.get_prop_mapping(ResourceProperties.PROP_1)
```

(Optional) Add alias mappings for each property - see [Adding Aliases](ADDING_ALIASES.md)

## 2. Create a Runner Class
A new subclass of the `RunnerWrapper` class is required to store how to actually run the query using openstacksdk. It
will also be the place where we can define extra parameters that can be used to fine-tune the query.

To add a Runner Class:
1. Create a new file under `/openstack_query/runners/` called `<resource>_runner.py` replace `<resource>` with openstack resource name you want to query
2.  Create the `<resource>Runner` class definition
   - class must inherit from `RunnerWrapper` abstract base class and implement abstract methods.

for example:
```python
class ResourceRunner(RunnerWrapper):
    ...
    # specify the openstacksdk resource type
    RESOURCE_TYPE = Resource

    def _parse_meta_params(
        self,
        conn: OpenstackConnection

        # define meta params that could be passed
        # they should all be optional, if no meta-params are passed, the query should still work with default values
        meta_param_1 = None,
        meta_param_2 = None,
        ...
    ):
        # Define logic here that will alter the keyword arguments that will be passed to the openstacksdk command
        # based on the meta-parameter values passed in. This method should return a dictionary which will be merged with
        # server-side filters and be used when calling the specific openstacksdk query which gets the resources being queried for
        ...

    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[ServerSideFilters] = None,
        **meta_params,
    )
        # Define logic here that will setup keyword arguments - merging server-side kwargs (filter_kwargs) and meta_param
        # and call run_paginated_query
        ...

        # here we call `run_paginated_query` with the "dummy" openstacksdk call "conn.compute.resource"
        # and we call it with key-word arguments, merging both filter_kwargs with parsed meta-params returned from
        # self._parse_meta_params

        # you can other types of queries/logic here - this is up to your discretion
        return self._run_paginated_query(conn.compute.resource, **{filter_kwargs, meta_params})
```

For example in `ServerRunner` we have meta_params: `all_projects`, `as_admin` and `from_projects`
The following needs to be done in `parse_meta_param`:
   - `all_projects` - if passed as `True`, it should set the query to run on all servers (on all projects)
     - mutually exclusive to `from_projects`, can only work if `as_admin` is also set
     - should pass `all_tenants=True` to `conn.compute.servers` - this is called (in `run_query()`)

   - `as_admin` - should set the query to run as an admin
     - doesn't set any parameters, but needs to be passed if `from_projects` or `all_projects` is also given
     - if not passed it will raise an error, this is used for a workaround as openstack will ignore `all_tenants=True` or
     `projects` if the credentials aren't admin creds and wrong info will be outputted.

   - `from_projects` - sets the projects to search in
     - user passes a list of server names or ids here to limit search by
     - if set, it should convert names to project ids and passes `projects=[<project-ids>]` to `conn.compute.servers`

see `runners/server_runner.py` to see the implementation details.


## 3. Create a Mapping Class

A new subclass of the `MappingInterface` class is required to store query mappings.

To add a Mapping Class:
1. Create a new file under `/openstack_query/mappings/` called `<resource>_mapping.py` replace `<resource>` with openstack resource name you want to query
2.  Create the `<resource>Mapping` class definition
   - class must inherit from `MappingInterface` abstract base class and implement abstract methods.
3. Update the enum holding query types `/enums/query/query_types.py` and add a Enum mapping to this Mapping class.
4. (Optional) Add alias mappings for the query type - see [Adding Aliases](ADDING_ALIASES.md)

### 3a. Set the Prop Enum class

Set the PropEnum class in `get_prop_mapping` like so:
```python
    @staticmethod
    def get_prop_mapping() -> Type[ResourceProperties]:
        return ResourceProperties
```

### 3b. Set the Runner class

Set the Runner class in `get_runner_mapping` like so:
```python
    @staticmethod
    def get_runner_mapping() -> Type[ResourceRunner]:
        return ResourceRunner
```

### 3c. Set chain mappings

See [CHAINING.md](CHAINING.md) for information on how chaining works

Define shared property mappings between this query and other queries that the library supports.
- ensure that both properties contain the same information

we can add mapping like so:
```python
    def get_chain_mappings():
        ...
        return {
            # Here we map the prop_1 enum stored in ResourceProperties to the user_id enum stored in UserProperties
            # These two properties MUST store the same info
            ResourceProperties.PROP_1: UserProperties.USER_ID,
        }
    ...
```

### 3d. Set the client_side_handlers
We must define which preset-property pair can be used together when calling `where()` on this Query class.

The `get_client_side_handlers` class is where we define these mappings.
This class creates a Dataclass called `QueryClientSideHandlers` from the mappings we define.

Here you must:
1. Evaluate which presets you want to the query to accept and which properties they should work on
2. You must add the presets like so:

```python

    def get_client_side_handlers() -> ServerSideHandler:
        ...
        return QueryClientSideHandlers(
            # generic_handler = set preset-property mappings that belong to generic presets
            # This is required - at least one preset mapping must be defined here
            generic_handler=ClientSideHandlerGeneric(
                {
                    # Line below maps EQUAL_TO preset on all available properties
                    # ["*"] - represents all props
                    QueryPresetsGeneric.EQUAL_TO: ["*"],
                    ...
                }
            ),
            # do the same for each of these (all optional)
            string_handler=ClientSideHandlerString(
               {
                    # Line Below maps MATCHES_REGEX preset on PROP_1 only
                    # All other properties are invalid
                    QueryPresetsString.MATCHES_REGEX: [ResourceProperties.PROP_1]
               }
            ),
            # we don't want any datetime presets to be valid - so set it to None
            datetime_handler=None,

            # we don't want any integer presets to be valid - so set it to None
            integer_handler=None
        )
    ...
```

## 3e (Optional) Map client-side filters

To add a server-side filter you must:
1. Read the Openstack API documentation for each Query the preset works on
    - links to the specific docs can be found in the docstring of `get_server_side_handler` method for the query
      - located in `mappings/<query-resource>_mapping.py`

2. Add a mapping like below - we map to a function that takes a set of user-defined args and creates a set of kwargs
    - can be a list of kwargs - in which case multiple calls will be made to openstack for each filter set returned.
    - This is the case for `ANY_IN` preset

```python

    def get_server_side_handler() -> ServerSideHandler:
        ...
        return ServerSideHandler(
            {
                # e.g. mapping a random server-side filter set to PROP_1 on matches regex
                QueryPresetsGeneric.MATCHES_REGEX: {
                    ResourceProperties.PROP_1: lambda value: {"pattern": value}
                }
            }
    ...
```


## 4. Create entry in query_objects.py

Now that the functionality has been added, you can make it available by creating a function in `query_objects` which
will call `QueryFactory` with the `ResourceMapping` class we just created.

e.g. Add this function to `openstack_query/api/query_objects.py` (as usual, replace `Resource` with the name of the openstack resource your querying)
```python
def ResourceQuery() -> QueryAPI:
   """
   Simple helper function to setup a query using a factory
   """
   # call the mapping class you just created - remember to import it as well!
   return get_common(ResourceMapping)

```

Then add this import to the top-level `__init__.py` - in `openstack_query/__init__.py`
```python
from .api.query_objects import ResourceQuery
```

Now you can use the new functionality like so

```python
from enums.query.props.resource_properties import ResourceProperties
from openstack_query import ResourceQuery

ResourceQuery().where(...).select(ResourceProperties.PROP_1).run("prod", meta_param1="abc", meta_param2="def")
```
