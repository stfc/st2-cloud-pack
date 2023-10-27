
### NOTE: Development work on ChatOps has been suspended

# Aliases and Chatops

A number of Aliases are pre-configured to allow listing of information using ChatOps. Aliases are a more human-readable
method of invoking these actions.

ChatOps requires Aliases to be defined for any Actions that ChatOps is allowed to invoke

- to define how bot reads, acknowledges, and responds to commands run via Slack

Currently Aliases have been written for `list` actions for `float.ip, hypervisor, project, server and user`

- NOTE: currently `user` list option can only give information on admin users (not stfc domain users) - it is not
  possible to list stfc users using `queryopenstack` library

An example of a list command is:

`!hypervisor list properties host_id, host_name, host_status preset host_disabled`

This command will list hypervisor ids, names and statuses for all disabled hypervisors

The command is explained below:

- `!hypervisor list` - run action `hypervisor.list`
- `properties host_id, host_name, host_status` - pass array [`host_id`, `host_name`, `host_status`]
  as `properties_to_select`
- `preset host_disabled` - use preset `host_disabled` to search

NOTE: currently Slack will only output results up to the maximum characters allowed for one post.

TODO: Provide a csv/txt file output attachment instead.
