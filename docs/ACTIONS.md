# Workflows
The following are orquesta workflow actions that are currently implemented.

NOTE: We have decided not to use orquesta going forward - mainly due to the difficulty with testing and
recovery - these workflows will be deprecated in favor of actions that do the same thing.

If you're a user, this won't affect you - we'll ensure that an action is created to replace any workflow we deprecate .


## Project workflows
workflows made to create pre-configured Openstack projects


| Workflow Name           | Description                                                                                           |
|-------------------------|-------------------------------------------------------------------------------------------------------|
| project.create.internal | Orquesta workflow to create a pre-configured Openstack Project to be used internally                  |
| project.create.external | Orquesta workflow to create a pre-configured Openstack project to be made available externally <br/>  |


## Check Workflow

workflows made to check certain things in OpenStack

| Workflow Name                    | Description                                                   |
|----------------------------------|---------------------------------------------------------------|
| workflow.checks.old.snapshots    | Checks for snapshots that were last updated before this month |
| workflow.checks.security.groups  | Checks for security groups that meet the given parameters     |


## Email Workflows (Deprecated)

The following are email workflows that are deprecated and need to be rewritten to use the
Query Library

| Workflow Name              | Description                                                                                 |
|----------------------------|---------------------------------------------------------------------------------------------|
| email.errored.server.users | Executes the email.server.users action for errored VMs to informing users about them        |
| email.shutoff.server.users | Executes the email.server.users action for shutoff VMs to informing users about them        |
| email.stale.server.users   | Executes the email.server.users action for VMs with an updated timestamp older than 90 days |


# Actions

Generally, Stackstorm openstack actions are written to be very similar and easy to understand for anyone who has used
Openstack CMD commands.

### Examples

examples of atomic Actions are shown below (not an exhaustive list):

| Action Name                | Description                                                                     |
|----------------------------|---------------------------------------------------------------------------------|
| floating.ip.create         | Action to assign a number of floating IP to a project                           |
| network.create             | Action to create a network for a project                                        |
| network.rbac.create        | Action to create Role Based Access Control rules on a network                   |
| project.create             | Action to create a new openstack project (not-configured)                       |
| project.show               | Action to find and list an Openstack Project's properties given it's Name or ID |
| quota.set                  | Action to set project quota                                                     |
| role.add                   | Action to add user role to a project                                            |
| router.add.interface       | Action to add interface to a router                                             |
| router.create              | Action to create a Openstack router                                             |
| security.group.create      | Action to create new security group for a project                               |
| security.group.list        | Action to list security groups and their properties for a given project         |
| security.group.rule.create | Action to create a new rule for a given security group                          |
| server.list                | Action to list server properties given some criteria                            |
| subnet.create              | Action to create an Openstack subnet                                            |
| user.get.email             | Action to get a user's email address given their Name/ID                        |


## Misc Openstack Actions


the following are miscellaneous openstack actions - (not `create`, `delete`, `update`, `show`)

| Action Name             | Description                                                                                                                                    |
|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| openstack.projects.sync | Duplicates projects and user rights between openstack instances. This action will only copy user rights for users that are in the STFC domain. |
| checks.old.snapshots    | Check For old volume snapshots in projects                                                                                                     |
| check.security.groups   | Check Security groups in projects for specific parameters                                                                                      |


## Atlassian Actions

the following are actions that interact with Atlassian

| Action Name             | Description                   |
|-------------------------|-------------------------------|
| atlassian.create.ticket | Creates tickets in atlassian. |


## Juptyer Actions

the following are actions related to STFC Cloud JuptyerHub Service

| Action Name                   | Description                                                                                     |
|-------------------------------|-------------------------------------------------------------------------------------------------|
| jupyter.server.start          | Starts servers for the given list of users                                                      |
| jupyter.server.stop           | Stops servers for the given list of users                                                       |
| jupyter.user.create           | Creates the given list of users                                                                 |
| jupyter.user.delete           | Removes the given list of users. This implicitly deletes any running pods the user has started. |
| workflow.jupyter.user.prepare | Creates a list of JupyterHub users, and starts up servers for each user                         |


## ChatOps Actions

The following are actions related to STFC Cloud Slack ChatOps

| Action Name         | Description                                                                                 |
|---------------------|---------------------------------------------------------------------------------------------|
| chatops.pr_reminder | Sends a HTTP Post request to a ChatOps endpoint to trigger reminders to the Slack workspace |


## Query Library (WIP)

The following are actions that use the query library.
- allows for more refined and complex searches than what openstack currently allows
- uses the `queryopenstack` library: see usage here: <link to queryopestack git>


NOTE: This is currently under development
- additional functionality to query other openstack resources needs to be added to Query Library
- more bespoke and complex query actions will also be written


| Action Name               | Description                                                          |
|---------------------------|----------------------------------------------------------------------|
| user.search.by.property   | Search for Openstack Users by specific property values               |
| user.search.by.regex      | Search for Openstack Users by specific property values using regex   |
| server.list               | Get all Servers                                                      |
| server.search.by.property | Search for Openstack Servers by specific property                    |
| server.search.by.regex    | Search for Openstack Servers by specific property values using regex |
| server.search.by.datetime | Search for Openstack Servers by relative time since created/updated  |


## Reboot/Disable Hypervisors (WIP)

the following are actions that reboot or disable hypervisors and schedule downtime in Icinga

NOTE: Under development - these may be broken

| Action Name                         | Description                                                         |
|-------------------------------------|---------------------------------------------------------------------|
| hypervisor.remove.icinga.downtime   | Removes all downtimes associated with a hypervisor                  |
| hypervisor.schedule.icinga.downtime | schedules downtime for nova-compute service on hypervisor           |
| hypervisor.service.disable          | disables hypervisor service in openstack                            |
| hypervisor.service.enable           | enables hypervisor service in openstack                             |
| hypervisor.reboot                   | (action workflow) disables hypervisor and schedules icinga downtime |


## Openstack List Actions (Deprecated)

The following are openstack list actions

NOTE: These actions are deprecated and need to be rewritten to use the Query Library

Each list action will be converted into actions similar to Query Library Actions:
- i.e. `floating.ip.list` will become `floating.ip.search.by.property`, `floating_ip.search.by.regex` etc

| Action Name      | Description                          |
|------------------|--------------------------------------|
| floating.ip.list | Lists floating ips by a query-preset |
| hypervisor.list  | Lists hypervisors by a query-preset  |
| image.list       | Lists images by a query-preset       |
| project.list     | Lists projects by a query-preset     |
| project.list     | Lists projects by a query-preset     |

### Correctness Actions (Deprecated)

The following are "correctness" actions that are used to find partially deleted resources.

Some work is needed to evaluate if these are still needed and if so - re-write them to use the Query Library

| Action Name                                            | Description                                                      |
|--------------------------------------------------------|------------------------------------------------------------------|
| correctness.find.floating.ips.in.non.existent.projects | Find non-existent projects referenced by floating ips            |
| correctness.find.images.in.non.existent.projects       | Find non-existent projects referenced by images                  |
| correctness.find.floating.ips.in.non.existent.projects | Find non-existent projects referenced by floating ips            |
| correctness.find.non.existent.floating.ips             | Find non-existent floating ips that are still listed in projects |
| correctness.find.non.existent.images                   | Find non-existent images that are still listed in projects       |
| correctness.find.non.existent.servers                  | Find non-existent servers that are still listed in projects      |
| correctness.find.servers.in.non.existent.projects      | Find non-existent projects referenced by servers                 |



## Email Actions (WIP)
Several emailing workflows have been added so CloudOps team can send emails to users easily

NOTE: Under development

| Action Name | Description                                       |
|-------------|---------------------------------------------------|
| email.test  | sends an email using the 'test' emailing template |

### Email Actions (Deprecated)
The following are email actions that are deprecated and need to be rewritten to use the
Query Library

| Workflow Name           | Description                                                                       |
|-------------------------|-----------------------------------------------------------------------------------|
| email.floating.ip.users | Sends email notifications to floating ip project contacts based on a given query. |
| email.image.users       | Sends email notifications to image project contacts based on a given query.       |
| email.server.users      | Sends email notifications to VM owners based on a given query.                    |
