# stackstorm-openstack-pack

A Stackstorm pack for running Openstack scripts built for the STFC Cloud team

### Pack Features

1. Handle creating Internal and External Projects in Openstack

2. Automatically list VM properties per user based on certain criteria
3. Query Openstack Resources (with Query Library)
   - allows running more complex queries than cli provides
   - get VM shutoff/error, older/younger than threshold etc.
4. Send Emails to Openstack Users

### In Progress Features

5. Create/Delete Openstack Resources
6. Reboot Hypervisors, schedule downtimes in Icinga
7. Stop/Restart/Reboot VMs
8. Other miscellaneous Openstack Commands



# Setup Pack

### Connecting To Openstack
Openstack openrc config file is required for this pack to work.

The openrc file must be stored in any of these locations (on the VM or host running StackStorm):
 - `/etc/openstack/clouds.yaml`
 - `/home/<user>/.config/openstack/clouds.yaml`

see how to install StackStorm here: https://docs.stackstorm.com/install/

Install the pack like so:
`st2 pack install https://github.com/stfc/st2-cloud-pack`


### Pack Configuration

You can either:

- Copy the configuration in [stackstorm_openstack.yaml.example](https://github.com/stfc/st2-cloud-pack/blob/main/stackstorm_openstack.yaml.example) to `/opt/stackstorm/configs/stackstorm_openstack.yaml` and change the values to work for you.


- Run `st2 pack config stackstorm_openstack` on your host after installation to use the stackstorm config script and follow the instructions


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
