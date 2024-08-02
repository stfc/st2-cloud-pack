from unittest.mock import NonCallableMock
import pytest

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError

from openstack_api.openstack_user import find_user
from enums.user_domains import UserDomains


def test_find_user_missing_user_identifier():
    """
    Checks a missing user identifier will raise correctly
    """
    mock_conn = NonCallableMock()
    mock_user_identifier = "  "
    mock_user_domain = UserDomains.STFC

    with pytest.raises(MissingMandatoryParamError):
        find_user(mock_conn, mock_user_identifier, mock_user_domain)


def test_find_user_success():
    """
    Checks that find_user returns the correct result
    """
    mock_conn = NonCallableMock()
    mock_user_identifier = "foo"
    mock_user_domain = UserDomains.STFC

    res = find_user(mock_conn, mock_user_identifier, mock_user_domain)

    mock_conn.identity.find_domain.assert_called_once_with("stfc", ignore_missing=False)

    mock_conn.identity.find_user.assert_called_once_with(
        "foo",
        domain_id=mock_conn.identity.find_domain.return_value.id,
        ignore_missing=True,
    )
    assert res == mock_conn.identity.find_user.return_value
