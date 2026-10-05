from unittest.mock import Mock, patch
import pytest
from apis.utils.weighers import calc_weight


@patch(
    "apis.utils.weighers.Weighers",
    new_callable=Mock,
    spec=["prop1", "prop2"],
    spec_set=True,
)
def test_calc_weight_set_weigh_fn(mock_weighers):
    mock_host = {"name": "host1", "prop1": 10, "prop2": 6}
    mock_weights = {"prop1": 0.25, "prop2": 1}

    instance = mock_weighers.return_value
    instance.prop1.return_value = -10
    instance.prop2.return_value = 6

    res = calc_weight(mock_host, mock_weights)

    instance.prop1.assert_called_once()
    instance.prop2.assert_called_once()

    assert res == 3.5


@patch(
    "apis.utils.weighers.Weighers",
    new_callable=Mock,
    spec=["propA"],
    spec_set=True,
)
def test_calc_weight_missing_weigh_fn(_mock_weighers):
    mock_host = {"name": "host1", "prop1": 10}
    mock_weights = {"prop1": 0.25}

    with pytest.raises(AttributeError):
        calc_weight(mock_host, mock_weights)
