# stackstorm-openstack-pack

A Stackstorm pack for running Openstack scripts:

1. Handle creating Internal and External Projects in Openstack
2. Automatically list VM properties per user based on certain criteria

- shutoff/error status, older/younger than threshold etc.

3. Create/Delete VMs
4. Reboot Hypervisors, schedule downtimes
5. Stop/Restart/Reboot VMs
6. Run miscellaneous Openstack Commands

# Setup Openstack

- Openstack openrc config file is required in order to run Openstack Commands. The openrc file must be stored
  in `etc/openstack/clouds.yaml` or `/home/<user>/.config/openstack/clouds.yaml`.
- Copy the configuration in [stackstorm_openstack.yaml.example](https://github.com/stfc/st2-cloud-pack/blob/main/stackstorm_openstack.yaml.example) to `/opt/stackstorm/configs/stackstorm_openstack.yaml and populate the values.

# Developer Instructions

This repository uses automated testing using GitHub actions.
Many steps are available to run locally with the following setup:

### Setup

- Clone this repository
- Install [pre-commit](https://pre-commit.com/#install). This will format your code
  on commit and in the future run many automated tests.
- If you are on Linux a helper script is included to setup and run Stackstorm unit tests.
  This is done by running `./run_tests.sh`
- Additionally, tests can be run locally using `pytest` through the IDE or CLI.

## General Development Notes

### Coding Standards

- Work must include appropriate unit tests to exercise the functionality (typically through mocking)
- All changes must pass through the PR process and associated CI tests
- The Black formatter enforces the coding style, rather than PEP8
- `main` should only include production ready, or disabled actions

Where possible we want to separate out the Stackstorm layer from our functionality.
This makes it trivial to test without having to invoke the ST2 testing mechanism.

For actions the architecture looks something like:

```
|actions or sensors| <-> | lib module | <-> | API endpoints |
```

This makes it trivial to inject mocks and tests into files contained within `lib`,
and allows us to re-use various API calls and functionality.

A complete example can be found in the following files:
[actions/jupyter](https://github.com/stfc/st2-cloud-pack/blob/main/actions/src/jupyter.py),
[lib/jupyter_api](https://github.com/stfc/st2-cloud-pack/blob/main/lib/jupyter_api/user_api.py)

and their associated tests:
[test_jupyter_actions](https://github.com/stfc/st2-cloud-pack/blob/main/tests/actions/test_jupyter_actions.py),
[test_user_api](https://github.com/stfc/st2-cloud-pack/blob/main/tests/lib/jupyter/test_user_api.py).

# Openstack Workflow

`project.create.internal` - Action Orquesta workflow to create a pre-configured Openstack Project to be used internally

1. Create Project
2. Then, run the following actions in parallel:

- Create security groups default, http and https
- Populate admin and stfc user list for project
- create default rbac policy

3. Then, configure security group rules for default, http and https after the respective security group is created

Required Parameters:

- `project_name`: Name of the project
- `project_description`: Description of the project
- `admin_user_list`: Array of users who must have admin access to the project
- `stfc_user_list`: Array of STFC users with access to the project

Optional Parameters:

- `network_name`: Network to create project on
  - default: Internal
- `default_network_internal_rules`: JSON of default network rules
  - default: (Taken from Datastore and decrypted)
- `http_network_internal_rules`: JSON of http network rules
  - default: (Taken from Datastore and decrypted)
- `https_network_internal_rules`: JSON of https network rules
  - default: (Taken from Datastore and decrypted)

`project.create.external` - Action Orquesta workflow to create a pre-configured Openstack project to be made available
externally

1. Create Project
2. Then, run the following actions in parallel:

- Create security group default
- Create external Network
- Set the quota for the project
- Populate admin and stfc user list for project

3. Once quota assigned, setup default external security rules
4. Once external network created:

- Create RBAC policy
- Create and configure Router and Subnet
- Assign float ips

Required Parameters:

- `project_name`: Name of the project
- `project_description`: Description of the project
- `network_name`: Name of network for project
- `network_description`: Description of network for project
- `subnet_name`: Name of subnet for project
- `subnet_description`: Description of subnet for project
- `router_name`: Name of router for project
- `router_description`: Description of router for project
- `ip_number`: Number of ips to assign to project
- `admin_user_list`: Array of users who must have admin access to the project
- `stfc_user_list`: Array of STFC users with access to the project

Optional Parameters:

- `default_network_external_rules`: JSON of default network rules
  - default: (Taken from Datastore and decrypted)
- `egress_external_ips`: Array of IPs to be given TCP/UDP egress rules
  - default: (Taken from Datastore and decrypted)

`send.server.email` - Action to email users information about their servers (Shutoff/Error VM
Reminders)

1. Perform a search on servers per user
2. Email each user the results of the search of servers that correspond to them

Required Parameters:

- `query_preset`: Name of preset query - i.e. server_shutoff etc

Optional Parameters:
`properties_to_select`: Properties to select for servers

- default: `["id", "name", "status", "user_name", "user_email"]`
  `message`: Message to send in the email
- default: `None`
  `subject`: String of email subject
- default: `Test Message`
  `header`: filepath to standard header file
- default: `/opt/stackstorm/packs/stackstorm_openstack/email_templates/header.html`
  `footer`: filepath to standard footer file
- default: `/opt/stackstorm/packs/stackstorm_openstack/email_templates/footer.html`
  `test_override`: Boolean, if true override sending email, instead sending to a test email address.
- default: `false`
  `test_override_email`: Email to send if `test_override` is set to true
- default: `None`
  `smtp_account`: smtp account name to use - must be configured in pack settings
- default: `default`
  `email_cc`: Array of email addresses to cc in
- default: `None` - not required
  `attachment_filepaths`: Array of filepaths for file attache=ments
- default: `None` - not required

## Openstack Check Workflows

`workflow.checks.old.snapshots`: Checks for snapshots that were last updated before this month.

Required parameters:

- `cloud_account` - The clouds.yaml account to use to connect to openstack
- One of:
  - `project_id` - The project to scan
  - `all_projects` - Toggle to scan the whole cloud

The following is required for creating tickets in atlassian. For more information see [Create Tickets](#create-tickets).

- `email` - The email of the account used to log into atlassian
- `api_key` - The api key of the account used to log into atlassian
- `servicedesk_id` - The service desk to create tickets in.
- `requesttype_id` - The request type to create tickets under.

`workflow.checks.security.groups`: Checks for security groups that meet the given parameters.

Required parameters:

- `ip_prefix` - The IP addresses that are allowed to access the given port range. Example: `0.0.0.0/0` for the whole internet.
- `max_port` - The upper limit of the port range.
- `min_port` - the lower limit of the port range.
- `cloud_account` - The clouds.yaml account to use to connect to openstack
- One of:
  - `project_id` - The project to scan
  - `all_projects` - Toggle to scan the whole cloud

The following is required for creating tickets in atlassian. For more information see [Create Tickets](#create-tickets).

- `email` - The email of the account used to log into atlassian
- `api_key` - The api key of the account used to log into atlassian
- `servicedesk_id` - The service desk to create tickets in.
- `requesttype_id` - The request type to create tickets under.

# Actions

Contains the following actions:
Generally, Stackstorm openstack actions are written to be very similar and easy to understand for anyone who has used
Openstack CMD commands

- generally each openstack resource `server, hypervisor, float.ip, etc` have 4 basic commands `create`, `delete`
  , `update`, `show`
  - NOTE: CURRENTLY MANY OF THESE METHODS - (ESPECIALLY CREATE AND DELETE) ARE NOT IMPLEMENTED, (AND MAY NOT BE IF
    THEY ARE NOT FEASIBLE/POSSIBLE UNDER CURRENT CONSTRAINTS IMPOSED BY THE CLOUD OPS TEAM)
  - they may also have other commands specific to them. `i.e. server.reboot, server.restart etc`

## Openstack List Actions

In addition, `hypervisor, server, user, float.ip and project` all have `list` actions:

- allows for more refined and complex searches than what openstack currently allows
- uses the `queryopenstack` library: see usage here: <link to queryopestack git>

## Openstack Actions

`openstack.projects.sync`: Duplicates projects and user rights between openstack instances. This action will only copy user rights for users that are in the STFC domain.

Required Parameters:

- `cloud` - The original cloud to copy projects and users from
- `dupe_cloud` - The secondary cloud to create the duplicated projects and user roles on.

## Reboot/Disable Hypervisor Actions

`hypervisor.remove.icinga.downtime`: Removes all downtimes associated with a hypervisor

Required Parameters:
`hypervisor`: Name or ID of hypervisor to remove downtimes for in Icinga

`hypervisor.schedule.icinga.downtime`: schedules downtime for `nova-compute` service on hypervisor

Required Parameters:
`hypervisor`: Name or ID of hypervisor to schedule downtimes for in Icinga
`start_time_unix`: Unix timestamp for start of downtime (ignored if timestamp string is given)
`end_time_unix`: Unix timestamp for end of downtime (ignored if timestamp string is given)

Optional Parameters:
`start_time_str`: timestamp in format `YYYY-MM-DD, HH:MM:SS` for start of downtime - default: `None` - not required
`end_time_str`: timestamp in format `YYYY-MM-DD, HH:MM:SS` for end of downtime - default: `None` - not required
`author`: `who scheduled the downtime`

- default: StackStorm
  `comment`: `reason for scheduling downtime`
- default: Scheduled using Stackstorm - reason not given
  `is_flexible`: if icinga downtime is flexible - default: `false`
  `flexible_duration`: if flexible downtime, duration in seconds - default: 0

`hypervisor.service.disable`: disables hypervisor service in openstack

- `nova-compute` is name of service for VMs, if given as `service_binary`, action only succeeds only if no servers
  currently being hosted by hypervisor
- TODO: Automated live migrations?

  Required Parameters:
  `hypervisor`: Name or ID of hypervisor to disable a service on
  `service_binary`: Name of service to disable

  Optional Parameters:
  `reason`: Reason to disable service

`hypervisor.service.enable`: enables hypervisor service in openstack Required Parameters:
`hypervisor`: Name or ID of hypervisor to enable a service on
`service_binary`: Name of service to enable

`hypervisor.reboot`:
action that:

1. Disables hypervisor (same process as hypervisor disable)
2. Schedules downtime on icinga TODO: convert to orquesta workflow

## Create Tickets

`atlassian.create.ticket`: Creates tickets in atlassian.
Required parameters:

- `email` - The email of the account used to log into atlassian
- `api_key` - The api key of the account used to log into atlassian
- `servicedesk_id` - The service desk to create tickets in. All tickets passed to the action will be created in this service desk. You cannot specify multiple service desks or different service desks for different tickets. You can find the list of service desks and their IDs at `<Your workspace>.atlassian.net/rest/servicedeskapi/servicedesk`
- `requesttype_id` - The request type to create tickets under. You can find the list of request types and their IDs at `<Your workspace>.atlassian.net/rest/servicedeskapi/servicedesk/<servicedesk_id>/requesttype`

Required for developers only:

- `tickets_info` - The dictionary of information that will be used to generate tickets. When using this action in a workflow you will need to pass the output of the previous action as an `object` type. The dictionary should include the same formatting as laid out below.
  - `title` - A python string with one or more sections to format. Example: `"This is the {p[title]}"`
  - `body` - A python string with one or more sections to format. Can be made entirely of the formatting section. Example: `"This is the {p[body]}, there has been a problem with {p[server]}"` or `"{p[body]}"`
  - `server_list` - A python list of arbitrary length. The list will include one or more dictionaries with the following keys.
    - `dataTitle` - The keys in this dictionary will be used to format the `title` entry. The keys can be called anything as long as they are included in the string in `title`. Example: `{"title": "This replaces the {p[title]} value!"}`.
    - `dataBody` - The keys in this dictionary will be used to format the `body` entry. The keys can be called anything as long as they are included in the string in `body`. Example `{"body": "This replaces the {p[body]} value", "server": "host2400"}`

# Rules

A number of rules are provided in this pack on a number of triggers defined in the `stackstorm_send_notifications` pack
to handle rabbitmq message commands.

## Hypervisor Rules

`rabbitmq.hypervisor.disable.service.rule`

- matches trigger `rabbit.message` with `message_type=HYPERVISOR_DISABLE_SERVICE` and calls `hypervisor.service.disable`
  using `stackstorm_send_notification.rabbit.execute`

`rabbitmq.hypervisor.enable.service.rule`

- matches trigger `rabbit.message` with `message_type=HYPERVISOR_ENABLE_SERVICE` and calls `hypervisor.service.enable`
  using `stackstorm_send_notification.rabbit.execute`

`rabbitmq.hypervisor.reboot.rule`

- matches trigger `rabbit.reply.message` with `message_type=HYPERVISOR_REBOOT` and calls `hypervisor.reboot`
  using `stackstorm_send_notification.rabbit.execute.and.reply`

`rabbitmq.hypervisor.schedule.icinga.downtime.rule`

- matches trigger `rabbit.message` with `message_type=HYPERVISOR_SCHEDULE_ICINGA_DOWNTIME` and
  calls `hypervisor.schedule.icinga.downtime` using `stackstorm_send_notification.rabbit.execute`

`rabbitmq.hypervisor.remove.icinga.downtime.rule`

- matches trigger `rabbit.message` with `message_type=HYPERVISOR_REMOVE_ICINGA_DOWNTIME` and
  calls `hypervisor.remove.icinga.downtime` using `stackstorm_send_notification.rabbit.execute`

## Server Rules

`rabbitmq.server.create.rule`

- matches trigger `rabbit.message` with `message_type=CREATE_VM` and calls `server.create`
  using `stackstorm_send_notification.rabbit.execute`

`rabbitmq.server.delete.rule`

- matches trigger `rabbit.message` with `message_type=DELETE_VM` and calls `server.delete`
  using `stackstorm_send_notification.rabbit.execute`

`rabbitmq.server.reboot.rule`

- matches trigger `rabbit.message` with `message_type=REBOOT_VM` and calls `server.reboot`
  using `stackstorm_send_notification.rabbit.execute`

# NOTE: May need to change this to a execute and reply version - depending on use case?

`rabbitmq.server.shutdown.rule`

- matches trigger `rabbit.message` with `message_type=SHUTDOWN_VM` and calls `server.shutdown`
  using `stackstorm_send_notification.rabbit.execute`

`rabbitmq.server.restart.rule`

- matches trigger `rabbit.message` with `message_type=RESTART_VM` and calls `server.restart`
  using `stackstorm_send_notification.rabbit.execute`

## Openstack rules

`openstack.deletedmachines.rule`

- matches trigger `openstack.deletingmachines` when a machine is stuck in the deleting state for more than 10m. Calls the `atlassian.create.tickets` action. The sensor for this rule runs every 7 days.

`openstack.loadbalancers.rule`

- matches trigger `openstack.loadbalancer` when a loadbalancer or amphora is not pingable or is reporting an error. Calls the `atlassian.create.tickets` action. The sensor for this rule runs every 7 days.

# Aliases and Chatops

A number of Aliases are pre-configured to allow listing of information using ChatOps. Aliases are a more human-readable
method of invoking these actions.

ChatOps requires Aliases to be defined for any Actions that ChatOps is allowed to invoke

- to define how bot reads, acknowledges, and responds to commands run via Slack

Currently Aliases have been written for `list` actions for `float.ip, hypervisor, project, server and user`

- NOTE: currently `user` list option can only give information on admin users (not stfc domain users) - it is not
  possible to list stfc users using `queryopenstack` library
- NOTE: currently, it takes 10mins to display server information

An example of a list command is:

`!hypervisor list properties host_id, host_name, host_status preset host_disabled`

This command will list hypervisor ids, names and statuses for all disabled hypervisors

The command is explained below:

- `!hypervisor list` - run action `hypervisor.list`
- `properties host_id, host_name, host_status` - pass array [`host_id`, `host_name`, `host_status`]
  as `properties_to_select`
- `preset host_disabled` - use preset `host_disabled` to search

NOTE: currently Slack will only output results up to the maximum characters allowed for one post. Look into providing a
csv/txt file output attachment instead.

# Misc

Other examples of atomic Actions are shown below (not an exhaustive list):
`floating.ip.create` - Action to assign a number of floating IP to a project
`network.create` - Action to create a network for a project
`network.rbac.create` - Action to create Role Based Access Control rules on a network
`project.create` - Action to create a new openstack project (not-configured)
`project.show` - Action to find and list an Openstack Project's properties given it's Name or ID
`quota.set` - Action to set project quota
`role.add` - Action to add user role to a project
`router.add.interface` - Action to add interface to a router
`router.create` - Action to create a Openstack router
`security.group.create` - Action to create new security group for a project
`security.group.list` - Action to list security groups and their properties for a given project
`security.group.rule.create` - Action to create a new rule for a given security group
`server.list` - Action to list server properties given some criteria
`subnet.create` - Action to create an Openstack subnet
`user.get.email` - Action to get a user's email address given their Name/ID

The Following are Orquesta workflows - which chain together a number of scripts:
