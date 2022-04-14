from unittest import mock
from unittest.mock import NonCallableMock

from nose.tools import raises

from openstack_wrappers.openstack_identity import (
    OpenstackIdentity,
    MissingMandatoryParamError,
)


@raises(MissingMandatoryParamError)
def test_project_and_domain_missing_throws():
    OpenstackIdentity().find_domain("")


def test_forwards_find_domain_result():
    instance = OpenstackIdentity()
    with mock.patch(
        "openstack_wrappers.openstack_identity.OpenstackConnection"
    ) as patched_connection:
        identity_api = patched_connection.return_value.__enter__.return_value.identity
        expected = NonCallableMock()

        found = instance.find_domain(expected)

        assert found == identity_api.find_domain.return_value
        identity_api.find_domain.assert_called_once_with(
            name_or_id=expected, ignore_missing=True
        )
