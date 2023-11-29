# Adding Actions

**NOTE: Many of our actions need to be refactored to use this guide**

This guide will go through how to add actions using `workflows` module and
`workflow_actions` as the entrypoint for your action


## 1. Write The Action script in Workflows

We recommend writing the script in `lib/workflows/email`
- `lib/workflows` contains scripts that validate and handle actions.
  - These scripts will make use of specific API modules also located in `lib`

- this is much easier to test than if this was handled in the actions layer.

The script's `main` function - the one that the Action will call must be named the same as the file itself
See example scripts in `lib/workflows/` to get an idea of how they work


## 2. Writing the Action config

See [Stackstorm Docs](https://docs.stackstorm.com/actions.html) for guidance on writing actions.
Action YAML configuration should be written to `actions` folder.


You need to set the entry_point for your Action to point to `src/workflow_actions.py`
And add two immutable parameters pointing to the submodule and file where your script is located
see example:


```yaml
  ...
  entry_point: src/workflow_actions.py # setting entry point
  ...
  parameters:
      ...

      submodule_name: # points to the submodule your script is located in `lib/workflows`
        default: email # here we're using the email submodule
        immutable: true
        type: string

      action_name: # point to the file that contains code to handle the action
        default: send_decom_flavor_email
        immutable: true
        type: string
```

**NOTE: use of submodules may be deprecated soon: https://github.com/stfc/st2-cloud-pack/pull/186**. In this case - you won't need to include `submodule_name`
