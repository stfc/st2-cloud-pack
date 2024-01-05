### Note: This is under active development
### TODO: The Query Library needs to be moved out of StackStorm and into a standalone repo

# Quick Links

User-related Docs:
  - [Usage](docs/user_docs/USAGE.md)
  - [API Reference](docs/user_docs/API.md)
  - [Presets Reference](docs/user_docs/PRESETS.md)

Feature References
  - [Servers](docs/user_docs/query_docs/SERVERS.md)
  - [Users](docs/user_docs/query_docs/SERVERS.md)
  - [Flavors](docs/user_docs/query_docs/FLAVORS.md)
  - [Projects](docs/user_docs/query_docs/PROJECTS.md)
  - [Hypervisors](docs/user_docs/query_docs/HYPERVISORS.md)

 Developer-related Docs:
- [Developer README](docs/developer_docs/OVERVIEW.md)
- [Chaining README](docs/developer_docs/CHAINING.md)


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
