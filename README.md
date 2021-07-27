# stackstorm-openstack-pack
A Stackstorm pack for running Openstack scripts:
1. Handle creating Internal and External Projects in Openstack
2. Automatically list VM properties per user based on certain criteria
  - shutoff/error status, older/younger than threshold etc.

# Actions
Contains the following actions:

Atomic actions that calls a python script:

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
`security.group.rule.create` - Action to create a new rule for a given security
group
`server.list` - Action to list server properties given some criteria
`subnet.create` - Action to create an Openstack subnet
`user.get.email` - Action to get a user's email address given their Name/ID

The Following are Orquesta workflows - which chain together a number of scripts:

`project.create.internal` - Action Orquesta workflow to create a pre-configured Openstack Project to be used internally
`project.create.external` - Action Orquesta workflow to create a pre-configured Openstack project to be made available externally
`send.server.email` - Action Orquesta workflow to email users information about their servers (Shutoff/Error VM Reminders)
