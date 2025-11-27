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

# CI/CD & Testing

we have several CI/CD jobs mostly on unittests and maintaining code styling and formatting. 
We run the following tools: 
- [black](https://github.com/psf/black) - for maintaining code formatting
- [pylint](https://pypi.org/project/pylint/) - static code analyzer
- [pytest](https://docs.pytest.org/en/stable/) - unittest framework 
- [coverage](https://coverage.readthedocs.io/en/7.12.0/) - to measure code coverage
- [codeql](https://codeql.github.com/) - static code analyzer for detecting vulnerabilities

## How test CI/CD works

We rely on upstream [stackstorm](https://github.com/stackstorm/st2) branch. 
Currently we're using a dev `v3.9` branch. 

To run the tests, we have to install stackstorm. 
We use the `./run_tests.sh` script to setup stackstorm and run all the tests.

## What to do if the CI/CD fails? 

CI/CD can fail for a number of reasons. Most commonly:

1. Tests fail - have a look at why the tests failed. 
You should run `run_tests.sh` locally to make sure the error isn't related to the CI/CD process  
2. Coverage fails 
If you're adding new functionality, make sure to add unittests to cover all the new code.
If you're removing functionality, this might be a false positive, which you can ignore
It is up to the Code owners discretion whether this failure matters

3. Dependencies can't be installed
Usually this is because of an upstream change. Since we're using a dev branch, this is more likely
Unfortunately there's no quick solution here, if upstream stackstorm releases a stable branch, you'll have
to switch to that by editing the envrionment variable `ST2_VERSION` in `run_tests.sh`