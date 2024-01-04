# Aliases

There are several Enums that represent different values that the user can provide as input.

These include:

1. Property Enums
   - which define the properties that can be extracted from an Openstack item
2. Preset Enums
   - which defines the query logic to use when calling `where`
3. Query Enum
   - which map to the different queries the library supports. Used when mapping one query to another like
   when calling `then` or `append_from`

## Adding an Alias

Aliases are optional, We don't need to include an alias for every Enum value, only where it makes sense to do so.

To add an alias, first find the specific Enum that contains the value you want to add an alias for.

This class should have a method called `_get_aliases`.

Edit this class to add a case for your alias. e.g:
```python
class ServerProperties(PropEnum):
    ...
    @staticmethod
    def _get_aliases():
        return {
            ...
            # adding "new_alias" as an alias which maps to server name
            ServerProperties.SERVER_NAME: ["vm_name", "name", "new_alias"]
        }
```

Your alias must be:
1. Unique - no other enum for that class must share that enum
2. Lowercase - so that we can compare in case-insensitive way
3. Intuitive - so it's easy to use

**NOTE:** You don't need to include the alias that matches the enum name exactly (case-insensitive) - in such cases
they will automatically be mapped over.
