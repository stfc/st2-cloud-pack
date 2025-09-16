# Adding Actions

This guide will go through how to add actions using `workflows` module and
`workflow_actions` as the entrypoint for your action


## 1. Write The Action script in Workflows

We recommend writing the script in `lib/workflows/`
- `lib/workflows` contains scripts that validate and handle actions.
  - These scripts will make use of specific API modules also located in `lib`

- this is much easier to test than if this was handled in the actions layer.

The script must contain a function with the same name as the file which the action will use as the entry-point.
In other words - this is the function that the Action will call and pass any user-defined inputs to.
See example scripts in `lib/workflows/` to get an idea of how they work


## 2. Writing the Action config

See [Stackstorm Docs](https://docs.stackstorm.com/actions.html) for guidance on writing actions.
Action YAML configuration should be written to `actions` folder.


You need to set the entry_point for your Action to point to `src/openstack_actions.py`
And add an immutable parameter pointing to the file where your script is located
see example:


```yaml
  ...
  entry_point: src/openstack_actions.py # setting entry point
  ...
  parameters:
      ...
      action_name: # point to the file that contains code to handle the action
        default: send_decom_flavor_email
        immutable: true
        type: string
```
