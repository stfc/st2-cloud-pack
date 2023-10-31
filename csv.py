"""This file write directories to a csv files
    based on the number of provided directories."""
from typing import Union, List, Dict

import csv
"""
Imports for the query libarary
"""
from openstack_query.api.query_objects import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enums.query.query_presets import QueryPresetsGeneric

def get_query():
    """
    Creates pulles a list from the query libary to be added to a cvs file.
    :param:
    :return:
    """

    data = ServerQuery().select(ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME, ServerProperties.SERVER_STATUS)

    data.sort_by((ServerProperties.SERVER_NAME, True))
    data.group_by(ServerProperties.SERVER_STATUS)

    data.run("openstack")

    return data


def to_csv_list(self, results: Union[List, Dict], data, output_filepath):
    """
    Takes a list of dictionaries and outputs them into a designated csv file 'self._parse_properties'
    :param data: this is the list of dictionaries passed in to this function
    :param output_filepath: this is the output path that is passed in to the function for it to use
    :return: Does it return anything.
    """

    if data and len(data) > 0:
        fields = data[0].keys()
    else:
        raise RuntimeError("data is empty")

    with open(output_filepath, "w", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

    return print("List Written to csv")


def to_csv_dictionary(self, results: Union[List, Dict], data, dir_path):
    """
        :Takes a dictionary of dictionaries and outputs them into separate designated csv file 'self._parse_properties'
        :param data: this is the dictionary of dictionaries passed in to this function
        :param dir_path: this is the output path the csv files will be created in
        :return: Does it return anything.
    """

    for p_id, p_info in data.items():
        file_path = f"{dir_path}{p_id}.csv"
        to_csv_list(p_info, file_path)

    return print("Dictionary written to csv")


def to_csv(self, results: Union[list, dict], data, filepath):
    """
        :Takes a dictionary of dictionaries or list of dictionaries and a filepath or directory path.
        :It then decides if the to_csv_list or to_csv_Dictionaries function is needed then call the required one.
        :param data: this is the dictionary of dictionaries or list of dictionaries that is passed in to other functions
        :param dir_path: this is the output path the csv files will be created in
        :return: Does it return anything.
    """

    # rewrite to use list/dict instead of filepath.spit(".")

    # path_type = filepath.split(".")

    data = get_query()

    if results == List:
        to_csv_list(data, filepath)
    else:
        to_csv_dictionary(data, filepath)
    return


if __name__ == "__main__":

    #Connect to main run area and move components and tests in the correct areas in the st2-cloud-pack

    result = get_query().to_list()
    fu = 2

#    example1 = [
#        {
#            "server_id": "server_id1",
#            "server_name": "server1",
#            "user_id": "user_id1",
#            "user_name": "user1"
#        },
#        {
#            "server_id": "server_id2",
#            "server_name": "server2",
#            "user_id": "user_id2",
#            "user_name": "user2"
#        }
#    ]
#    OUTPUT_FILEPATH = "./path/to/file.csv"
#    to_csv(example1, OUTPUT_FILEPATH)

#    example2 = {
#        "user_name is user1": [
#            {
#                "server_id": "server_id1",
#                "server_name": "server1",
#                "user_id": "user_id1",
#                "user_name": "user1",
#            },
#            {
#                "server_id": "server_id2",
#                "server_name": "server2",
#                "user_id": "user_id1",
#                "user_name": "user1",
#            },
#        ],
#        "user_name is user2": [
#            {
#                "server_id": "server_id3",
#                "server_name": "server3",
#                "user_id": "user_id2",
#                "user_name": "user2",
#            },
#            {
#                "server_id": "server_id4",
#                "server_name": "server4",
#                "user_id": "user_id2",
#                "user_name": "user2",
#            },
#        ],
#    }

    # uncomment this part to test example 2
#    OUTPUT_DIR_PATH = "./path/to/"
#    to_csv_grouped(example2, OUTPUT_DIR_PATH)

#    pats = get_csv_directory(OUTPUT_FILEPATH)
#    print(pats)
