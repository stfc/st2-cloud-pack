import csv

import openstack
from openstack.exceptions import ResourceNotFound
from tabulate import tabulate


# Utility functions for query_openstack module

# Functions:
#     create_openstack_connection(string, string)
#     validate_input_list([string], [string])
#     output_to_console([{key:value}])
#     output_to_file([{key:value}])


def create_openstack_connection(cloud_name="openstack", region_name="RegionOne"):
    """
    Get Openstack connection
        (gets properties from ~/.config/openstack/clouds.yaml)

        Parameters:
                cloud_name (string): name of cloud in yaml script to use (default 'openstack')
                region_name (string): name of region in yaml script to use (defailt 'RegionOne')
        Returns: (openstack.connection.Connection object): openstack connection object
    """
    return openstack.connect(cloud=cloud_name, region_name=region_name)


def validate_input_list(list_to_check, valid_list):
    """
    Separate a list_to_check into valid and invalid lists - based on contents of valid_list

        Parameters:
                list_to_check ([string]): list to validate
                valid_list ([string]): list of all valid examples
        Returns: ([list], [list]): tuple of two distinct sublists containing valid
        or invalid entries respectively
    """
    valid, invalid = [], []
    if list_to_check:
        for input_property in list_to_check:
            if input_property in valid_list:
                valid.append(input_property)
            else:
                invalid.append(input_property)
    return valid, invalid


def output_to_console(results_dict_list):
    """
    Output a result of query to console - prints table using tabulate

        Parameters:
            results_dict_list (list of dictionaries: [{}]) - a list of dictionaries
            representing the query results
        Returns: None
    """
    if results_dict_list:
        header = results_dict_list[0].keys()
        rows = [row.values() for row in results_dict_list]
        print(tabulate(rows, header))
    else:
        print("none found")


def output_to_file(save_path, results_dict_list):
    """
    Write results of query into a file
        - csv format:
            - whitespace as delimeter
            - saves as file specified openstack_resource save_path

        Parameters:
            save_path (string) - file path to save results
        Returns: None
    """
    if results_dict_list:
        keys = results_dict_list[0].keys()
        try:
            with open(save_path, "w", encoding="utf-8", newline="\n") as output_file:
                writer = csv.DictWriter(output_file, keys)
                writer.writeheader()
                writer.writerows(results_dict_list)
        except ResourceNotFound as err:
            print(f"could not create file {err}")
    else:
        print("none found - no file made")
