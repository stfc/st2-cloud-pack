
# Instructions

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

See the README in `/lib/openstack_query/README.md`

This will soon be extracted out into a separate repo soon.
