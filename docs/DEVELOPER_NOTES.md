# ST2 Cloud Pack Overview

This is an Openstack pack that is used by the STFC Cloud. It contains a collection of Openstack "runbook" scripts that
help with day-to-day management of the Cloud.

The Pack is currently under development, quite a bit of refactoring is still to be done.

## Pack Structure

### Actions, Rules and Sensors folders

As with all StackStorm Packs, this Pack contains Actions, Rules and Sensors.

#### Actions

Actions are located in the `actions` folder
    - each yaml file contains configuration for each action the pack supports
    - the `src` subfolder contains a Python code that handles an action, parses it and forwards it to functions in the
`lib` layer .


#### Orquesta Workflows

We have several Orquesta workflows implemented `actions/workflows`

We only use orquesta workflows for simple workflows - forwarding output from one action to another.

We don't use orquesta to:
1. Perform complex logic
2. Using operators like `for` or `if` where it can be helped
3. Parse any data - must forward onto a python function to handle parsing
4. Store any state - workflows must be stateless if at all possible

This is because we cannot easily test orquesta workflows and so complex logic should be handled in Python files that
can be unit-tested separately


#### Rules and Sensors

Several Sensors and Corresponding rules have been created for the pack and are used infrequently, this is an area we
aim to improve upon as use-cases are found. Our primary aim is to refactor and settle upon a good selection of Actions
that can be run manually before automating using Sensors and Rules

#
### Lib Folder

Most of the implementation details for the pack's actions can be found in the `lib` folder.

This folder contains several python submodules - which each implement APIs that the pack's actions call.

There are currently 7 API submodules (under `apis`:

1. Email API - This API is responsible for sending emails, and handling email-related actions.
   - see [EMAIL_API.md](EMAIL_API.md) for details

2. Openstack API - The Largest API - responsible for handling Openstack actions (which includes a majority of the pack's action).
   - This API, more than any of the others, requires major refactoring - and is a WIP

3. Openstack Query API - A python library developed by the Cloud Team to make querying Openstack easier.
   - See [Openstack Query README.md](https://github.com/stfc/openstack-query-library/blob/main/README.md)

4. Icinga API (deprecated) - This API is responsible for handling actions related to Icinga alerts
   - we no longer use Icinga in favor of Prometheus and Alertmanager

5. Alertmanager API - this API is responsible for handling actions related to Alertmanager alerts

6. SSH API - a simple API that exposes a single `exec_command` function for running various scripts on our hypervisors
    - scripts that can be run are placed on the hosts

7. Jira API - this API is responsible for handling actions related to JSM


NOTE: we're aware that packs exist for Jira, SSH, openstack etc. We decided to maintain our own code for these services
so we can write complex workflows and customise them to work for our team


### `lib/workflows` folder

`lib/workflows` contains the entrypoints to many complex actions. It is our way of stringing together multiple smaller
actions like Orquesta but allows us to add unittests

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
