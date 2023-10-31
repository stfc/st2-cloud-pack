import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from csv import to_csv
from csv import to_csv_list
from csv import to_csv_dictionary

@pytest.fixture
def example_grouped_data():
    return {
        "user_name is user1": [
            {
                "server_id": "server_id1",
                "server_name": "server1",
                "user_id": "user_id1",
                "user_name": "user1",
            },
            {
                "server_id": "server_id2",
                "server_name": "server2",
                "user_id": "user_id1",
                "user_name": "user1",
            },
        ],
        "user_name is user2": [
            {
                "server_id": "server_id3",
                "server_name": "server3",
                "user_id": "user_id2",
                "user_name": "user2",
            },
            {
                "server_id": "server_id4",
                "server_name": "server4",
                "user_id": "user_id2",
                "user_name": "user2",
            },
        ],
    }

@pytest.fixture
def example_data():
    return [
        {
            "server_id": "server_id1",
            "server_name": "server1",
            "user_id": "user_id1",
            "user_name": "user1"
        },
        {
            "server_id": "server_id2",
            "server_name": "server2",
            "user_id": "user_id2",
            "user_name": "user2"
        }
    ]


@patch("builtins.open", new_callable=mock_open)
@patch("csv.DictWriter")
def test_to_csv_with_valid_parameters(mock_dict_writer, mock_file, example_data):
    """With Valid Parameters"""
    to_csv(example_data, "test")

    mock_file.assert_called_once_with("test", "w", encoding="utf-8")
    mock_dict_writer.assert_called_once_with(
        mock_file.return_value, fieldnames=example_data[0].keys()
    )
    mock_dict_writer.return_value.writeheader.assert_called_once()
    mock_dict_writer.return_value.writerows.assert_called_once_with(example_data)


def test_to_csv_fails():
    with pytest.raises(RuntimeError):
        to_csv([], "test")


@patch("main.to_csv")
def test_to_csv_grouped_loop_empty_input(mock_to_csv):

    """loop is given: 0 Items"""
    mock_to_csv.assert_not_called()


@patch("main.to_csv")
def test_to_csv_grouped_loop_one_input(mock_to_csv):
    """mock to_cs outputs"""

    example_grouped_data = {
        "user_name is user1": [
            {
                "server_id": "server_id1",
                "server_name": "server1",
                "user_id": "user_id1",
                "user_name": "user1",
            },
            {
                "server_id": "server_id2",
                "server_name": "server2",
                "user_id": "user_id1",
                "user_name": "user1",
            },
        ],
    }

    """Run To csv"""
    to_csv_dictionary(example_grouped_data, "test")

    """loop is given: 1 Items"""
    mock_to_csv.assert_called_once_with(example_grouped_data["user_name is user1"], Path("test/user_name is user1.csv"))


@patch("main.to_csv")
def test_to_csv_grouped_loop_more_than_one_input(mock_to_csv, example_grouped_data):
    """mock to_cs outputs"""

    """Run To csv"""
    to_csv_dictionary(example_grouped_data, "test")

    """
    loop is given: 1 Items
    This bit need rewriting to check for multiple outputs instead of 1.
    """
    mock_to_csv.assert_called_with(example_grouped_data["user_name is user2"], Path("test/user_name is user2.csv"))

