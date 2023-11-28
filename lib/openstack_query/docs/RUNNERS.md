
# Query Runners
Query runners refer to the class that is responsible for actually running the query.
Each Query has an associated Runner Class and inherits from `MappingInterface`


## Query Meta-Parameters

This is the name given to extra parameters that can be passed in when you call `run()` which
can be used to determine the behaviour of the query.


Some meta-parameters may be universal - available to act on all queries. These include:

`None (so far)`

Other meta-parameters may be exclusive to the query type

### Meta Parameter Reference

`ServerQuery`: `run()` meta parameters

| Parameter Definition       | Optional?            | Description                                                                                                                                                                                                                                                               |
|----------------------------|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `from_projects: List[str]` | Yes                  | A list of project IDs or Names to limit search to<br/>Optional, if not given will run search in project given in clouds.yaml.<br/><br />Searching for specific projects in Openstack may not be possible without admin credentials - `as_admin` needs to be set to True ) |
| `all_projects: Bool`       | Yes, default = False | If True, will run query on all available projects available to the current user - set in clouds.yaml. <br/><br /> Searching for specific projects in Openstack may not be possible without admin credentials - `as_admin` needs to be set to True )                       |
| `as_admin: Bool`           | Yes, default = False | If True, will run the query as an admin - this may be required to query outside of given project context set in clouds.yaml. <br/><br /> Make sure that the clouds.yaml context user has admin privileges                                                                 |


`UserQuery`: `run()` meta parameters

| Parameter Definition                                           | Optional? | Description                                                                                                                                                                                                                                  |
|----------------------------------------------------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `from_domain: UserDomains` <br/><br/>(see `/enums/user_domains`) | Yes       | A User Domain to limit User query to<br/>Optional, if not given will run search on DEFAULT_DOMAIN - `UserDomains.STFC` <br/><br /> NOTE: it is possible to specify user domain via `where()` - if both are provided then an error is raised) |


`ProjectQuery`: `run()` meta parameters
`None (so far)`

`FlavorQuery`: `run()` meta parameters
`None (so far)`

**NOTE: PROVIDING ANY OTHER VALUES EXCEPT FOR THE ONES MENTIONED ABOVE WILL EITHER BE IGNORED (or an error will be raised)**
- even if they are valid params for the openstacksdk call - this is to prevent unexpected behaviour.

### 1. Adding a meta-param

If you want to add meta-param functionality, it's a good idea to check whether it can be done already by using
the API commands provided - i.e. `where()`, `sort_by()`, `group_by()`. We favor using the API rather than meta-params
since they are harder to document well and could be confusing

To add a metaparam you need to locate the runner class associated for the resource you want to change.
- located in `openstack_query/runners/<resource>_runner` - replace `<resource>` with the resource name you want to change - i.e. `server`

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
