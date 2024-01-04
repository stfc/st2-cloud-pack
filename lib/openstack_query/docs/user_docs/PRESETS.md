# Query Presets

Presets define how the query filters results when using the `where()` command

Presets define what query to run, they must be as atomic as possible - e.g. `EQUAL_TO`, `NOT_EQUAL_TO`, etc.
This allows the query to be defined by multiple presets and makes it clear what you want the query to find.

**Example:** To find all servers in a list of projects which are shutoff or errored - the queries can be:
```python
q1 = ServerQuery().where(preset=ANY_IN, prop=project_id, values=["project1", "project2"])
q2 = q1.where(preset=ANY_IN, prop=server_status, values=["ERROR", "SHUTOFF"])
```

Presets are stored as enums. There are currently the following enum classes:

| Preset Class                                  | Description                                                                   |
|-----------------------------------------------|-------------------------------------------------------------------------------|
| [QueryPresetsGeneric](#QueryPresetsGeneric)   | Used to hold presets that can be applied to any property (no matter the type) |
| [QueryPresetsString](#QueryPresetsString)     | Used to hold presets that can only be applied to string-type properties       |
| [QueryPresetsInteger](#QueryPresetsInteger)   | Used to hold presets that can only be applied to integer-type properties      |
| [QueryPresetsDateTime](#QueryPresetsDateTime) | Used to hold presets that can only be appli                                   |


## Importing presets

Presets can be imported like so:
```python
from enums.query.query_presets import QueryPresetsGeneric, QueryPresetsString, QueryPresetsInteger, QueryPresetsDateTime
```

**NOTE: WIP - Not implemented yet**

Alternatively, you can also pass string aliases instead of a preset Enum (see reference below).
(These are case-insensitive)

# Reference

## QueryPresetsGeneric
QueryPresetsGeneric has the following presets:

| Preset       | Aliases           | Description                                                                          | Extra Parameters                                              |
|--------------|-------------------|--------------------------------------------------------------------------------------|---------------------------------------------------------------|
| ANY_IN       | "in"              | Finds objects which have a property matching any of a given set of values            | `values: List` - a list of property values to compare against |
| NOT_ANY_IN   | "not in"          | Finds objects which have a property that does not match any of a given set of values | `values: List` - a list of property values to compare against |
| EQUAL_TO     | "equal", "=="     | Finds objects which have a property matching a given value                           | `value` - a single value to compare against                   |
| NOT_EQUAL_TO | "not equal", "!=" | Finds objects which have a property that does not match a given value                | `value` - a single value to compare against                   |


## QueryPresetsString
QueryPresetsString has the following presets:

| Preset        | Aliases                | Description                                                      | Extra Parameters                                                    |
|---------------|------------------------|------------------------------------------------------------------|---------------------------------------------------------------------|
| MATCHES_REGEX | "regex", "match_regex" | Finds objects which have a property that matches a regex pattern | `value: str` - a string which can be converted into a regex pattern |


## QueryPresetsInteger
QueryPresetsInteger has the following presets:

| Preset                   | Aliases | Description                                                                             | Extra Parameters                                                              |
|--------------------------|---------|-----------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| GREATER_THAN             | `None`  | Finds objects which have an integer/float property greater than a threshold             | `value: Union[int, float]` - an integer or float threshold to compare against |
| LESS_THAN                | `None`  | Finds objects which have an integer/float property less than a threshold                | `value: Union[int, float]` - an integer or float threshold to compare against |
| GREATER_THAN_OR_EQUAL_TO | `None`  | Finds objects which have an integer/float property greater than or equal to a threshold | `value: Union[int, float]` - an integer or float threshold to compare against |
| LESS_THAN_OR_EQUAL_TO    | `None`   | Finds objects which have an integer/float property less than or equal to a threshold    | `value: Union[int, float]` - an integer or float threshold to compare against |


## QueryPresetsDateTime
QueryPresetsDateTime has the following presets:

| Preset                   | Aliases | Description                                                                                            | Extra Parameters |
|--------------------------|---------|--------------------------------------------------------------------------------------------------------|------------------|
| OLDER_THAN               | `None`  | Finds objects which have an datetime property older than a given relative time threshold               | see below        |
| YOUNGER_THAN             | `None`  | Finds objects which have an datetime property younger than a given relative time threshold             | see below        |
| OLDER_THAN_OR_EQUAL_TO   | `None`  | Finds objects which have an datetime property older than or equal to a given relative time threshold   | see below        |
| YOUNGER_THAN_OR_EQUAL_TO | `None`  | Finds objects which have an datetime property younger than or equal to a given relative time threshold | see below        |

### Extra Parameters
- `days: int` - (Optional) relative number of days since current time to compare against
- `hours: int` - (Optional) relative number of hours since current time to compare against
- `minutes: int` - (Optional) relative number of minutes since current time to compare against
- `seconds: int` - (Optional) relative number of seconds since current time to compare against

**NOTE:** At least one parameter from above must be given with a non-zero value for the preset to work, otherwise an error is produced
