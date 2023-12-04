# Other workflows
This file contains other workflows/instructions for adding new parts to the query library

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

## Adding a meta-param to an existing Runner class

Runners refer to the class that is responsible for actually running the query.
Each Query has an associated Runner Class and inherits from `MappingInterface`.
- located in `openstack_query/runners/<resource>_runner` - replace `<resource>` with the resource name you want to change - i.e. `server`


If you want to add meta-param functionality, it's a good idea to check whether it can be done already by using
the API commands provided - i.e. `where()`, `sort_by()`, `group_by()`.

We favor using the API rather than meta-params since they are harder to document well and could be confusing


To add a metaparam you need to locate the runner class associated for the resource you want to change.

Then edit the `_parse_meta_params` method

```python
def _parse_meta_params(
    self,
    conn: OpenstackConnection,
    ...
    # place your parameters here.
) -> Dict:
    # place your logic for meta-parameters here

```

**NOTE: when editing an existing query's meta-params - YOU MUST MAKE SURE THE NEW PARAM IS OPTIONAL - so as to not break other already existing workflows**
    - you can do this by providing a default value.

The `_parse_meta_params` method returns a dictionary that can be ultimately merged with server-side key-word arguments in the `run_query` method.
This new dictionary can then be passed to the openstacksdk call.

To add any extra logic that merges these two dictionaries together, you will need to also alter the `run_query` method.
