from abc import ABC
from typing import Dict, List, Union
from unittest.mock import Mock, NonCallableMock

from st2tests.actions import BaseActionTestCase


# pylint: disable=too-few-public-methods
class OpenstackActionTestBase(BaseActionTestCase, ABC):
    def get_action_instance(
        self,
        config=None,
        api_mocks: Union[Mock, Dict[str, Mock]] = None,
    ):
        """
        Wraps get action instance allowing a developer to additionally
        inject OpenStack Mock APIs too
        @param config: Optional Additional config to pass in
        @param api_mock: The prepared mock to inject
        @param additional_mocks: Additional prepared mocks to inject
        @return: The action with a mock (or a default mock) injected
        """
        if config is None:
            config = {}

        # This is intentionally non-callable (despite being a callable type)
        # to ensure we never attempt to hit the real API in any test case

        # If you are here because of an error, you need to inject your mock
        # through api_mocks, instead of relying on implicit mocks.
        if isinstance(api_mocks, Mock):
            api_mocks = api_mocks if api_mocks else NonCallableMock()
            config["openstack_api"] = api_mocks
        elif isinstance(api_mocks, Dict):
            for key, mock in api_mocks.items():
                mock = mock if mock else NonCallableMock()
                config[key] = mock
        elif api_mocks:
            raise TypeError(f"Invalid type of '{type(api_mocks)}' for 'api_mocks'")

        return super().get_action_instance(config=config)

    def _test_run_dynamic_dispatch(self, expected_methods: List[str]):
        for method_name in expected_methods:
            assert hasattr(self.action, method_name)
            mocked_method = Mock()
            setattr(self.action, method_name, mocked_method)

            expected_kwargs = {"foo": NonCallableMock(), "bar": NonCallableMock()}
            return_value = self.action.run(submodule=method_name, **expected_kwargs)

            mocked_method.assert_called_once_with(**expected_kwargs)
            assert return_value == mocked_method.return_value
