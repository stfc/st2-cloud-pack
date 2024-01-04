# Adding New Preset To An Existing Preset Group

## **1. Add the preset name to the corresponding enum class in `/lib/enums/query/query_presets.py`**

e.g.
```python
class QueryPresetsGeneric(QueryPresets):
    """
    Enum class which holds generic query comparison operators
    """

    EQUAL_TO = auto()
    ...
    NEW_PRESET = auto() # <- we add this line to repesent a new preset enum belonging to the 'Generic' group
```

(Optional) Add alias mappings for the preset - see [Adding Aliases](ADDING_ALIASES.md)

## **2. Edit the corresponding handler class in `/lib/openstack_query/handlers/client_side_handler_<preset-group>.py`.**

Here you must:
- add a 'client-side' filter function as a method
- add the mapping between the enum and filter function in self._filter_functions.

The filter function must:
- **take as input at least one parameter - `prop`**:
  - `prop` (must be the first positional argument) - represents the property value the filter acts on.
  - Can also take other parameters are extra arguments that are required for the preset to work
- **return a boolean**
   - `True` if the prop passes filter
   - `False` if not

e.g. editing `client_side_handler_generic.py`
```python
class ClientSideHandlerGeneric(ClientSideHandler):
...

def __init__(self, filter_function_mappings: PresetPropMappings):
   super().__init__(filter_function_mappings)

   self._filter_functions = {
       QueryPresetsGeneric.EQUAL_TO: self._prop_equal_to,
       ...
       QueryPresetsGeneric.NEW_PRESET: self._new_preset_filter_func # <- 2) add the enum-to-function mapping
   }

...

def _new_preset_filter_func(self, prop: Any, arg1, arg2):
   """
   A new preset filter - takes a property value, performs some logic and returns a boolean if
   property passes a filter or not
   :param prop: property value to check
   :param arg1: some arg the filter uses
   :param arg2: some other arg the filter uses
   :returns: True or False
   """
   ... # Define your preset logic here
```

## **3. Edit the query class mappings for each Query class you wish to use the preset in**
Each Query Class has a set of mappings which configures certain aspects of the Query (See [FILTER_MAPPINGS.md](FILTER_MAPPINGS.md) for details).

One of these aspects is which preset-property pair can be used together when calling `where()` on the class.

Here you must:
1. Evaluate which Query class should be able to use your new preset
2. For each Query class you've chosen, evaluate which property(ies) the preset should work on
3. Add chosen mappings to `get_client_side_handlers` method in the Mappings class for each chosen Query
   - these are located in `mappings/<query-resource>_mapping.py`

e.g. Adding Mappings for `QueryPresetsGeneric.NEW_PRESET` to `ServerQuery`. Editing `mappings/server_mapping.py`
```python

class ServerMapping(MappingInterface):
    ...

    @staticmethod
    def get_client_side_handlers() -> ServerSideHandler:
        ...
        return QueryClientSideHandlers(
            # set generic query preset mappings
            generic_handler=ClientSideHandlerGeneric(
                {
                    # Line below maps EQUAL_TO preset on all available properties
                    # ["*"] - represents all props
                    QueryPresetsGeneric.EQUAL_TO: ["*"],
                    ...
                    # Line below maps our 'new preset' to two properties which the preset can run on
                    # Running the preset on any other property leads to an error
                    QueryPresetsGeneric.NEW_PRESET: [
                        ServerProperties.SERVER_ID,
                        ServerProperties.SERVER_NAME
                    ]
                }
            ),
        )
    ...
```

## **4. (Optional) Add server-side filters for the preset**

To add a server-side filter you must:
1. Read the Openstack API documentation for each Query the preset works on
    - links to the specific docs can be found in the docstring of `get_server_side_handler` method for the query
      - located in `mappings/<query-resource>_mapping.py`

2. Once a server-side filter is discovered for your new preset add a mapping to `get_server_side_handler` method
e.g. Adding server-side mapping for `QueryPresetsGeneric.NEW_PRESET` to `ServerQuery`. Editing `mappings/server_mapping.py`
```python

class ServerMapping(MappingInterface):
    ...

    @staticmethod
    def get_server_side_handler() -> ServerSideHandler:
        ...
        return ServerSideHandler(
            {
                QueryPresetsGeneric.NEW_PRESET: {
                    # adding a server-side mapping for NEW_PRESET when given SERVER_ID
                    ServerProperties.SERVER_ID: lambda value, arg1, arg2:
                        {"server-side-kwarg": value, "server-side-arg1": arg1, "server-side-arg2": arg2}
                }
            }
    ...
```

# **Adding a new preset group**

As stated above - presets are grouped based on the datatype of the property the act on. If you need another preset
group - you can add one like so:

1. Create a new preset group class in `/lib/enums/query/query_presets.py`
    - it inherits from base class QueryPresets


2. Create new client side handler in `/lib/openstack_query/handlers/client_side_handler_<preset>.py`
   - it inherits from base class `ClientSideHandler` - `/lib/openstack_query/handlers/client_side_handler.py`.


3. Add your preset as a attribute in query_client_side_handlers dataclass
   - located in `/lib/structs/query/query_client_side_handlers.py`


4. Follow steps mentioned above to add new presets to the new preset group class you've created

5. Edit `QueryPresets` type declaration at the bottom of the file `/lib/enums/query/query_presets.py` and add your new
preset ffclass to it
