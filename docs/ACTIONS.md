# Workflows

NOTE: this may not be an exhaustive list - see `actions/workflows` for all available workflows in stackstorm under this pack

| Workflow Name    | Description                                     |
|------------------|-------------------------------------------------|
| hypervisor.drain | Migrates servers off of the given hypervisor(s) |


## Actions

NOTE: this may not be an exhaustive list - see `actions` for all available actions in stackstorm under this pack

| Action Name                                         | Description                                                                                                                 |
|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| chatops.pr_reminder                                 | Sends a HTTP Post request to a ChatOps endpoint to trigger reminders to the Slack workspace                                 |
| check.internal.router.gateways                      | Check for routers with gateway address on the internal network                                                              |
| project.create                                      | Create a pre-configured Openstack Project for a specific flavor                                                             |
| email.test                                          | Sends a test email                                                                                                          |
| email.ops.down.disabled.hypervisors                 | Sends an email about down and disabled hypervisors                                                                          |
| email.users.with.decom.flavors                      | Sends an email to inform users that they have VMs running on flavors that are to be decommissioned                          |
| email.users.with.decom.images                       | Sends an email to inform users that they have VMs running images that are to be decommissioned                              |
| email.users.with.errored.vms                        | Sends an email to inform users that they have VMs in Errored state                                                          |
| email.users.with.shutoff.vms                        | Sends an email to inform users that they have VMs in Shutoff state                                                          |
| email.users.with.errored.vms                        | Sends an email to inform users that they have VMs in Errored state                                                          |
| email.users.with.vms.on.hv.fault.notification       | Sends an email to inform users that they have VMs on a faulty hypervisor                                                    |
| email.users.with.vms.on.hv.maintenance.notification | Sends an email to inform users that they have VMs on a hypervisor requiring maintenance                                     |
| group.add.user                                      | Add a user directly to a given group                                                                                        |
| hv.compute.service.disable                          | Disables the nova compute service on a hypervisor                                                                           |
| hv.compute.service.enable                           | Enables the nova compute service on a hypervisor                                                                            |
| hv.create.test.server                               | Build a test server on a given hypervisor, can optionally test all possible flavors avaliable to the hypervisor             |
| hv.downtime                                         | Schedule a downtime a Hypervisor in Icinga and AlertManager, mutes all alerts for the hypervisor                            |
| hv.find.empty                                       | Find hypervisors that have no VMs running on them                                                                           |
| hv.patch.reboot                                     | Patch and Reboot a hypervisor                                                                                               |
| hv.post.reboot                                      | Post reboot action                                                                                                          |
| hv.search.by.expression                             | Search for hypervisors with a selected expression                                                                           |
| hv.search.by.property                               | Search for hypervisors by specific property                                                                                 |
| hv.search.by.regex                                  | Search for hypervisors by specific property values using regex                                                              |
| icinga.remove.downtime                              | Remove a downtime for Host or Service in Icinga                                                                             |
| icinga.schedule.downtime                            | Schedule a downtime for Host or Service in Icinga                                                                           |
| icinga.search.by.name                               | Search Icinga for Hosts/Services by name                                                                                    |
| icinga.search.by.state                              | Search Icinga for Hosts/Services in a given state                                                                           |
| image.search.by.datetime                            | Query images based on a datetime property (e.g. created-at or last-updated)                                                 |
| image.search.by.expression                          | Search for images with a selected expression                                                                                |
| image.search.by.property                            | Search for images with a selected property matching, or not matching given value(s)                                         |
| image.search.by.regex                               | Search for image property using regex pattern, or not matching given value(s)                                               |
| image.share.to.project                              | Share an image to a project                                                                                                 |
| jira.create.task                                    | Create a test jira task                                                                                                     |
| jira.request.new.project                            | Creates a new Project in OpenStack. This requires an associated JIRA ticket, for manual Project creation see project.create |
| project.add.group.with.role                         | Add a pre-created group to a given project with given role                                                                  |
| project.add.user.with.role                          | Add a user directly to a given project with given role                                                                      |
| project.create                                      | create a pre-configured openstack project                                                                                   |
| project.delete                                      | delete a project                                                                                                            |
| project.remove.user.role                            | Removes a role from a user's project permissions                                                                            |
| project.search.by.property                          | Search for projects with a selected property matching, or not matching given value(s)                                       |
| project.search.by.regex                             | Search for projects property using regex pattern, or not matching given value(s)                                            |
| quota.set                                           | set a project quota                                                                                                         |
| server.create                                       | Create a new server                                                                                                         |
| server.list                                         | List all servers                                                                                                            |
| server.migrate                                      | Migrate a server to a new host                                                                                              |
| server.search.by.property                           | Search for Openstack Servers by specific property                                                                           |
| server.search.by.regex                              | Search for Openstack Servers by specific property values using regex                                                        |
| server.search.by.datetime                           | Search for Openstack Servers by relative time since created/updated                                                         |
| ssh.remote.command                                  | Execute command on a remote host                                                                                            |
| user.search.by.property                             | Search for user with a selected property matching, or not matching given value(s)                                           |
| user.search.by.regex                                | Search for users property using regex pattern, or not matching given value(s)                                               |
