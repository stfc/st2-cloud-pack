from abc import ABC
from unittest.mock import Mock, NonCallableMock

from st2tests.actions import BaseActionTestCase


class OpenstackActionTestCase(BaseActionTestCase, ABC):
    def get_action_instance(self, config=None, api_mock: Mock = None):
        if config is None:
            config = dict()

        # This is intentionally non-callable (despite being a callable type)
        # to ensure we never attempt to hit the real API in any test case

        # If you are here because of an error, you need to inject your mock
        # through api_mock, instead of relying on implicit mocks.
        api_mock = api_mock if api_mock else NonCallableMock()
        config["openstack_api"] = api_mock
        return super().get_action_instance(config=config)
