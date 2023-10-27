# stackstorm-openstack-pack

A Stackstorm pack for running Openstack scripts built for the STFC Cloud team

### Documentation Links

- [Rules](https://github.com/stfc/st2-cloud-pack/blob/main/RULES.md)
- [Actions](https://github.com/stfc/st2-cloud-pack/blob/main/ACTIONS.md)
- [ChatOps](https://github.com/stfc/st2-cloud-pack/blob/main/CHATOPS.md)
- [Contributing](https://github.com/stfc/st2-cloud-pack/blob/main/CONTRIBUTING.md)
- [Developer Notes](https://github.com/stfc/st2-cloud-pack/blob/main/DEVELOPER_NOTES.md)

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
