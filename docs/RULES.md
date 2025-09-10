# Rules

A number of rules are provided in this pack:

| Rule                          | Description                                                                                                             |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| alert.router.internal.gateway | Sends Jira Ticket when a Router with an Internal gateway address is found                                               |
| chatops.pr.reminder.global    | Send a global reminder request every Monday and Wednesday at 9AM to the ChatOps application                             |
| chatops.pr.reminder.personal  | Send a personal reminder request every Monday at 9AM to the ChatOps application                                         |
| hv.compute.service.disable    | Triggers the disable action when the hypervisor state changes from 'RUNNING' to 'PENDING MAINTENANCE'                   |
| hv.drain.for.maintenance      | Drains a hypervisor for patching                                                                                        |
| hv.patch.reboot               | Starts the patch reboot action when the hypervisor is drained                                                           |
| hv.post.reboot                | Removes the scheduled downtime, removes the alertmanager silence and enables the hv in openstack when the hv is back up |
| install.from.git.branch       | Installs a pack when a commit is pushed to a branch                                                                     |
| jira.request_new_project      | Handles JIRA issues requesting OpenStack project creation.                                                              |
| webhook.server.migrate        | Uses the webhook to live migrate the server.                                                                            |
