# Chaining

A feature that the query library adds is the ability to chain queries together.

Chaining, in this context means taking the results of a query, and using them to configure and run another query
    - be it on the same resource, or on another resource.

## Reference
This section shows what queries can be chained together. Applies for both `then()` and `append_from()`

`ServerQuery` available chains

| Prop 1                      | Prop 2                       | Type        | Maps                            |
|-----------------------------|------------------------------|-------------|---------------------------------|
| ServerProperties.USER_ID    | UserProperties.USER_ID       | Many-to-One | `ServerQuery` to `UserQuery`    |
| ServerProperties.PROJECT_ID | ProjectProperties.PROJECT_ID | Many-to-One | `ServerQuery` to `ProjectQuery` |
| ServerProperties.FLAVOR_ID  | FlavorProperties.FLAVOR_ID   | Many-to-One | `ServerQuery` to `FlavorQuery`  |


`UserQuery` available chains

| Prop 1                 | Prop 2                   | Type        | Maps                         |
|------------------------|--------------------------|-------------|------------------------------|
| UserProperties.USER_ID | ServerProperties.USER_ID | One-to-Many | `UserQuery` to `ServerQuery` |


`ProjectQuery` available chains

| Prop 1                       | Prop 2                      | Type        | Maps                            |
|------------------------------|-----------------------------|-------------|---------------------------------|
| ProjectProperties.PROJECT_ID | ServerProperties.PROJECT_ID | One-to-Many | `ProjectQuery` to `ServerQuery` |


`FlavorQuery` available chains

| Prop 1                     | Prop 2                     | Type        | Maps                           |
|----------------------------|----------------------------|-------------|--------------------------------|
| FlavorProperties.FlAVOR_ID | ServerProperties.FLAVOR_ID | One-to-Many | `FlavorQuery` to `ServerQuery` |


## QueryTypes
`then()` and `append()` take a QueryTypes enum or (equivalent alias) which represents the Query you want to chain into

| QueryTypes Enum Aliases | Equivalent Enum        | Represents Query |
|-------------------------|----------------| |
| FLAVOR_QUERY            | QueryTypes.FLAVOR_QUERY  | `FlavorQuery`|
| PROJECT_QUERY           | QueryTypes.PROJECT_QUERY | `ProjectQuery`|
| SERVER_QUERY            | QueryTypes.SERVER_QUERY  | `ServerQuery`|
| USER_QUERY              | QueryTypes.USER_QUERY    | `UserQuery`|

further aliases are WIP

## How then() works

The diagram below shows how we can use `then()` to perform chaining between two different Openstack Resources.
`then()` will return the new query, shunting any results into new query if `keep_previous_results = True`
see [API.md](API.md) for usage details

![Diagram showing how then() works when going from ServerQuery to UserQuery](./imgs/then-workflow.png)

Here, `then()` finds all unique values of `user_id` from the results of the first `ServerQuery` query.
Using these, it sets up a `UserQuery` with a pre-defined `where()` call - selecting for `user_ids` match
what was returned in the first query

`get_chain_mappings` holds how to map the query to other queries. Which we look for in `ServerMapping`

## How append_from() works

The diagram below show how we can use `append_from()` to perform chaining between two different Openstack Resources.
`append_from()` will run a separate query internally, and shunt the results into original query, it will return the original query
see [API.md](API.md) for usage details

![Diagram showing how append_from() works when going from ServerQuery to UserQuery](./imgs/append-from-workflow.png)

Here, `append_from()` works almost identically to `then()`, only this time, it runs a `select` selecting for specified
properties - e.g `user_name` that belong to `UserQuery`. This is then returned and concatenated into results via
`ResultContainer` class as `forwarded_props`.



## Shared common properties

A shared common property is are pairs of properties that hold the same information between two different openstack
resources. These properties can either:
1. Map one-to-Many. e.g. `UserQuery` to `ServerQuery`
- the shared common property is `user_id`
- A User can have many associated servers - so in this case one `user_id` can map to multiple servers


2. Map Many-to-one. e.g. going backwards from `ServerQuery` to `UserQuery`
- The shared common property is still `user_id`

Query Library supports both instances.


### Keeping Previous Results

A common workflow may want to keep certain results from previous chained queries (see [API.md](API.md) for how to do that)

- `append_from` will automatically forward selected values as `forwarded_props` to results
- `then` gives the user the option to

**Note Many-to-one property chaining can lead to duplicates** - this is left to the user to sort out


## Workflows


#### 1. Adding a new shared property Mapping

Before adding a shared property mapping - ensure that both properties contain the same information

1. Edit the `<resource>_mapping.py` file located in `opentack_query/mappngs`
2. Locate the method `get_chain_mappings` and add chain mappings.

we can add mapping like so:
```python
class ServerMapping(MappingInterface):

    @staticmethod
    def get_chain_mappings():
        ...
        return {
            # Here we map the user_id enum stored in ServerProperties to the user_id enum stored in UserProperties
            # These two properties store the same info - NOTE: enums that map together do not require same name
            ServerProperties.USER_ID: UserProperties.USER_ID,
            ... # add a new chain mapping here - the key must be a ServerProperties enum
        }
    ...
```

## Successive Chaining and Multi-step chaining
The query library has functionality to allow multi-step chaining - this is currently left for the user to implement
    - via successive `then()` chaining.

If we find that there are workflows that require successive chaining - we can add it as a `pattern` - this is a WIP
