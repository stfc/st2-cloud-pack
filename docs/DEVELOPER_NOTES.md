# ST2 Cloud Pack Overview

This is an Openstack pack that is used by the STFC Cloud. It contains a collection of Openstack "runbook" scripts that
help with day-to-day management of the Cloud.

The Pack is currently under development, quite a bit of refactoring is still to be done.

## Pack Structure

### Actions, Rules and Sensors folders

As with all StackStorm Packs, this Pack contains Actions, Rules and Sensors.

#### Actions

Actions are located in the `actions` folder - holding yaml configuration for each action the pack supports, along with a `src` folder.
The `src` folder contains a Python code that handles an Action or a collection of Actions.
- the main purpose of these handlers is to validate inputs and forward onto API methods held in `lib` folder
- we aim to simplify much of these files in favor of `workflows` - see below.

#### Orquesta Workflows

We have several Orquesta workflows implemented `actions/workflows` - mainly to create and configure projects in Openstack.

We have decided that moving forward, we will not be using Orquesta workflows as they are hard to unittest.

#### Rules and Sensors

Several Sensors and Corresponding rules have been created for the pack and are used infrequently, this is an area we
aim to improve upon as use-cases are found. Our primary aim is to refactor and settle upon a good selection of Actions
that can be run manually before automating using Sensors and Rules

#
### Lib Folder

Most of the implementation details for the pack's actions can be found in the `lib` folder.

This folder contains several python submodules - which each implement APIs that the pack's actions call.

There are currently 4 API submodules:

1. Email API - This API is responsible for sending emails, and handling email-related actions.
   - see [EMAIL_API.md](EMAIL_API.md) for details


2. Jupyter API - This API is responsible for handling actions related to our JupyterHub instance.
   - see [JUPYTER_API.md](JUPYTER_API.md) for details


3. Openstack API - The Largest API - responsible for handling Openstack actions (which includes a majority of the pack's action).
   - This API, more than any of the others, requires major refactoring - and is a WIP
   - see [OPENSTACK_API.md](OPENSTACK_API.md) for details


4. Openstack Query API - A python library developed by the Cloud Team to make querying Openstack easier.
   - This is in active development, and we're aiming to move this out of this pack to be a standalone library.
   - See [Openstack Query README.md](https://github.com/stfc/openstack-query-library/blob/main/README.md)


There are also several folders which contain shared components used by multiple API submodules.

1. `custom_types` - contains Python Type Declarations for submodules
2. `enums` - contains Enums used throughout the pack
3. `exceptions` - contains exception declarations that are used throughout the pack for custom error messages
4. `structs` - contains dataclasses that are used throughout the pack

Many of these folders contain information that really should be tightly coupled to the API module
    - see issue [188](https://github.com/stfc/st2-cloud-pack/issues/188)


### `lib/workflows` folder

`lib/workflows` module contains standalone scripts that handle stackstorm Actions that have `workflow_actions.py` as
their entrypoint.

`workflow_actions.py` is aimed to be the simplest StackStorm Action handler possible.
It's job is to:
- Forward user-defined inputs from the Web UI to a script in `workflows`.
- Evaluate and forward StackStorm-specific stored info - like pack config info

We aim to convert all existing and new actions to use `workflow_actions` to simplify code structure.
See issue [189](https://github.com/stfc/st2-cloud-pack/issues/189) for details


### TODO Folder

A set of Actions/Workflows that need to be implemented. These would be good-first issues!

Many of them currently there are waiting to be re-implemented using the Query Library and workflows


# Development Setup Instructions

This repository uses automated testing using GitHub actions.
Many steps are available to run locally with the following setup:

### Setup

- Clone this repository
- Install [pre-commit](https://pre-commit.com/#install). This will format your code
  on commit and in the future run many automated tests.
- If you are on Linux a helper script is included to setup and run Stackstorm unit tests.
  This is done by running `./run_tests.sh`
- Additionally, tests can be run locally using `pytest` through the IDE or CLI.


## Coding Standards

for code standards - see [CONTRIBUTING.md](CONTRIBUTING.md)

more specifically, for the cloud pack:
1. Work must include appropriate unit tests to exercise the functionality (typically through mocking)
2. All changes must pass through the PR process and associated CI tests
3. The Black formatter enforces the coding style, rather than PEP8
4. `main` should only include production ready, or disabled actions

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


## Query Library
We've implemented a python package to allow querying for OpenStack resources.
This is built on top of the standard openstacksdk library and implements more query features, and allows running
more complex queries.

See the Query Library [README.md](https://github.com/stfc/openstack-query-library/blob/main/README.md)

This will soon be extracted out into a separate repo soon.
