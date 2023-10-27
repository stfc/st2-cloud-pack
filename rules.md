# Rules

A number of rules are provided in this pack on a number of triggers defined in the `stackstorm_send_notifications` pack
to handle rabbitmq message commands.

## Hypervisor Rules

| Rule      | Description |
| ----------- | ----------- |
| `rabbitmq.hypervisor.disable.service.rule` | matches trigger `rabbit.message` with `message_type=HYPERVISOR_DISABLE_SERVICE` and calls `hypervisor.service.disable` using `stackstorm_send_notification.rabbit.execute`|
| `rabbitmq.hypervisor.enable.service.rule` | matches trigger `rabbit.message` with `message_type=HYPERVISOR_DISABLE_SERVICE` and calls `hypervisor.service.disable` using `stackstorm_send_notification.rabbit.execute`|
| `rabbitmq.hypervisor.enable.service.rule` | matches trigger `rabbit.message` with `message_type=HYPERVISOR_ENABLE_SERVICE` and calls `hypervisor.service.enable` using `stackstorm_send_notification.rabbit.execute`|
| `rabbitmq.hypervisor.reboot.rule` | matches trigger `rabbit.reply.message` with `message_type=HYPERVISOR_REBOOT` and calls `hypervisor.reboot` using `stackstorm_send_notification.rabbit.execute.and.reply` |
|`rabbitmq.hypervisor.schedule.icinga.downtime.rule`| matches trigger `rabbit.message` with `message_type=HYPERVISOR_SCHEDULE_ICINGA_DOWNTIME` and calls `hypervisor.schedule.icinga.downtime` using `stackstorm_send_notification.rabbit.execute`|
| `rabbitmq.hypervisor.remove.icinga.downtime.rule` | matches trigger `rabbit.message` with `message_type=HYPERVISOR_REMOVE_ICINGA_DOWNTIME` and calls `hypervisor.remove.icinga.downtime` using `stackstorm_send_notification.rabbit.execute` |

## Server Rules

| Rule      | Description |
| ----------- | ----------- |
| `rabbitmq.server.create.rule`| matches trigger `rabbit.message` with `message_type=CREATE_VM` and calls `server.create` using `stackstorm_send_notification.rabbit.execute` |
| `rabbitmq.server.delete.rule` | matches trigger `rabbit.message` with `message_type=DELETE_VM` and calls `server.delete` using `stackstorm_send_notification.rabbit.execute` |
| `rabbitmq.server.reboot.rule` | matches trigger `rabbit.message` with `message_type=REBOOT_VM` and calls `server.reboot` using `stackstorm_send_notification.rabbit.execute`|

# NOTE: May need to change this to a execute and reply version - depending on use case?

| Rule      | Description |
| ----------- | ----------- |
| `rabbitmq.server.shutdown.rule` | matches trigger `rabbit.message` with `message_type=SHUTDOWN_VM` and calls `server.shutdown` using `stackstorm_send_notification.rabbit.execute` |
| `rabbitmq.server.restart.rule` | matches trigger `rabbit.message` with `message_type=RESTART_VM` and calls `server.restart` using `stackstorm_send_notification.rabbit.execute` |

## Openstack rules

| Rule      | Description |
| ----------- | ----------- |
| `openstack.deletedmachines.rule` | matches trigger `openstack.deletingmachines` when a machine is stuck in the deleting state for more than 10m. Calls the `atlassian.create.tickets` action. The sensor for this rule runs every 7 days. |
| `openstack.loadbalancers.rule` | matches trigger `openstack.loadbalancer` when a loadbalancer or amphora is not pingable or is reporting an error. Calls the `atlassian.create.tickets` action. The sensor for this rule runs every 7 days. |
