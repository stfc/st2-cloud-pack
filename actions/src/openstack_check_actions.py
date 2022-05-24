import json
import os
import requests
import logging
import sys
from typing import Dict, Callable
from datetime import datetime
from openstack_api.openstack_connection import OpenstackConnection
from openstack_action import OpenstackAction
from requests.auth import HTTPBasicAuth

class CheckActions(OpenstackAction):

    def __init__(self, *args,**kwargs):
        """Constructor Class"""
        super().__init__(*args, **kwargs)

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)


    def check_project(self, project: str, cloud: str, max_port: int, min_port: int, ip_prefix: str):
        """
        Does the logic for security_groups_check, should not be invoked seperately.
        """
        rules_with_issues = []

        with OpenstackConnection(cloud_name=cloud) as conn:
            sec_group = conn.list_security_groups(filters={"project_id":project})
        for group in sec_group:
            for rules in group["security_group_rules"]:

                if rules["remote_ip_prefix"] == ip_prefix and rules["port_range_max"] == max_port and rules["port_range_min"] == min_port:
                    ruledict = {}
                    print("Issue with rule "+rules["security_group_id"])
                    ruledict["id"] = rules["security_group_id"]
                    ruledict["server_list"] =[]

                    with OpenstackConnection(cloud_name=cloud) as conn:
                        servers = conn.list_servers(filters={"all_tenants":True, "project_id": project}) #Using the inbuilt all_projects variable throws a connection issue, may have to change to projects in a future cloud upgrade

                    for server in servers:

                        with OpenstackConnection(cloud_name=cloud) as conn:
                            applied = conn.list_server_security_groups(server.id)

                        for serv_groups in applied:

                            if serv_groups["id"] == rules["security_group_id"]:
                                print("Rule is applied")
                                rules_with_issues.append({
                                    "dataTitle":{
                                        "id": server["id"]
                                    },
                                    "dataBody":{
                                        "proj_id": project,
                                        "sec_id": serv_groups["id"]
                                    }
                                })
                            else:
                                print("Rule not applied to "+server["id"])
        return rules_with_issues

    def security_groups_check(self, cloud_account: str, max_port: int, min_port: int, ip_prefix: str, project_id=None, all_projects=False):
        """
        Starts the script to check projects, can choose to go through all projects or a single project.

        Params:
        Cloud (Required): The name of the cloud to open from clouds.yaml

        Requires one of:
            all_projects (optional): Boolean for checking all projects, defaults to False
            project (optional): ID of project to check
        """

        #all_servers.filter(location.project.id=project)

        #print(servers.get_all_servers())
        rules_with_issues = {
            "title": "Server {p[id]} has an incorrectly configured server group",
            "body": "Project id: {p[proj_id]}\nSecurity Group ID: {p[sec_id]}",
            "server_list":[]
        }

        if all_projects:
            with OpenstackConnection(cloud_name=cloud_account) as conn:
                projects = conn.list_projects()
            for project in projects:
                output = self.check_project(project=project, cloud=cloud_account, max_port=max_port, min_port=min_port, ip_prefix=ip_prefix)
                rules_with_issues["server_list"] = output
        else:
            output = self.check_project(project=project_id, cloud=cloud_account, max_port=max_port, min_port=min_port, ip_prefix=ip_prefix)
            rules_with_issues["server_list"] = output

        return rules_with_issues

    def deleting_machines_check(self, cloud_account: str, project_id=None, all_projects=False):
        output = {
            "title": "Server {p[id]} has not been updated in more than 10 minutes during {p[action]}",
            "body": "The following information may be useful\nHost id: {p[id]} \n{p[data]}",
            "server_list": []
        }

        if all_projects:
            with OpenstackConnection(cloud_name=cloud_account) as conn:
                projects = conn.list_projects()
            for project in projects:
                deleted = self.check_deleted(project=project, cloud=cloud_account)
            output["server_list"] = deleted
        else:
            deleted = self.check_deleted(project=project_id, cloud=cloud_account)
            output["server_list"] = deleted

        return output

    def check_deleted(self, cloud: str, project: str):
        output = []
        with OpenstackConnection(cloud_name=cloud) as conn:
            server_list = conn.list_servers(filters={"all_tenants":True, "project_id": project})
        #Loop through each server in the project/list
        for i in server_list:
            #Take current time and check difference between updated time
            sinceUpdate = datetime.utcnow() - datetime.strptime(i.updated, '%Y-%m-%dT%H:%M:%Sz')
            #Check if server has been stuck in deleting for too long. (uses the last updated time so if changes have been made to the server while deleting the check may not work.)
            if i.status == "deleting" and sinceUpdate.total_seconds() >= 600:
                #Append data to output array
                output.append({
                "dataTitle":{"id": str(i.id), "action": str(i.status)},
                "dataBody":{"id": i.id, "data": json.dumps(i)}
                })

        return output

    def loadbalancer_check(self, cloud_account: str):

        with OpenstackConnection(cloud_name=cloud_account) as conn:
            amphorae = requests.get("https://openstack.nubes.rl.ac.uk:9876/v2/octavia/amphorae", headers={'X-Auth-Token': conn.auth_token}) 
        try:
            amph_json = amphorae.json()
        except requests.exceptions.JSONDecodeError:
            logging.critical(msg="There was no JSON response \nThe status code was: "+str(amphorae.status_code)+"\nThe body was: \n"+str(amphorae.content))
            return "There was no JSON response \nThe status code was: "+str(amphorae.status_code)+"\nThe body was: \n"+str(amphorae.content)
        output = {
            "title": "{p[title_text]}",
            "body": "The loadbalance ping test result was: {p[lb_status]}\nThe status of the amphora was: {p[amp_status]}\nThe amphora id is: {p[amp_id]}\nThe loadbalancer id is: {p[lb_id]}",
            "server_list": []
        }
        if amphorae.status_code == 403:
            #Checks user has permissions to access api
            logging.critical("Please run this script using a cloud admin account.")
            return "Please run this script using a cloud admin account."
        if amphorae.status_code == 200:
            #Gets list of amphorae and iterates through it to check the loadbalancer and amphora status.
            for i in amph_json["amphorae"]:
                status = self.check_status(i)
                ping_result = self.ping_lb(i['lb_network_ip'])

                if status[0] == 'error' or ping_result == 'error':
                    if status[0].lower() == 'error' and ping_result.lower() == 'error':
                        output["server_list"].append({
                            "dataTitle":{
                                "title_text": "Issue with loadbalancer "+ str(i['loadbalancer_id'] or "null")+" and amphora "+str(i['id'] or "null"),
                                "lb_id": str(i['loadbalancer_id'] or "null"),
                                "amp_id": str(i["id"] or "null")
                            },
                            "dataBody":{
                                "lb_status": str(ping_result or "null"),
                                "amp_status": str(status[1] or "null"),
                                "lb_id": str(i['loadbalancer_id'] or "null"),
                                "amp_id": str(i["id"] or "null")
                            }
                        }
                        )
                    elif status[0].lower() == 'error':
                        output["server_list"].append({
                            "dataTitle":{
                                "title_text": "Issue with loadbalancer "+ str(i['loadbalancer_id'] or "null"),
                                "lb_id": str(i['loadbalancer_id'] or "null"),
                            },
                            "dataBody":{
                                "lb_status": str(ping_result or "null"),
                                "amp_status": str(status[1] or "null"),
                                "lb_id": str(i['loadbalancer_id'] or "null"),
                                "amp_id": str(i["id"] or "null")
                            }
                        }
                        )
                    elif ping_result.lower() == 'error':
                        output["server_list"].append({
                            "dataTitle":{
                                "title_text": "Issue with amphora "+str(i['id'] or "null"),
                                "amp_id": str(i["id"] or "null"),
                            },
                            "dataBody":{
                                "lb_status": str(ping_result or "null"),
                                "amp_status": str(status[1] or "null"),
                                "lb_id": str(i['loadbalancer_id'] or "null"),
                                "amp_id": str(i["id"] or "null")
                            }
                        }
                        )
                else:
                    logging.info(i['id']+" is fine.")

        else:
            #Notes problem with accessing api if anything other than 403 or 200 returned
            logging.critical("We encountered a problem accessing the API")
            logging.critical("The status code was: "+str(amphorae.status_code))
            logging.critical("The JSON response was: \n"+str(amph_json))
            sys.exit()
        return output

    def check_status(self, amphora):
        #Extracts the status of the amphora and returns relevant info
        status = amphora['status']
        if status in ('ALLOCATED', 'BOOTING', 'READY'):
            return ['ok', status]
        
        return ['error', status]

    def ping_lb(self, ip):
    #Runs the ping command to check that loadbalancer is up
        response = os.system("ping -c 1 "+ip) #Might want to update to subprocess as this has been deprecated

        #Checks output of ping command
        if response == 0:
            logging.info(msg="Successfully pinged " + ip)
            return 'success'

        logging.info(msg=ip + " is down")
        return 'error'

    def check_notify_snapshots(self, cloud_account: str, project_id=None, all_projects=False):
        output = {
            "title": "Project {p[name]} has an old volume snapshot",
            "body": "The volume snapshot was last updated on: {p[updated]}\nSnapshot name: {p[name]}\nSnapshot id: {p[id]}\nProject id: {p[project_id]}",
            "server_list": []
        }
        if all_projects:
            with OpenstackConnection(cloud_name=cloud_account) as conn:
                projects = conn.list_projects()
            for project in projects:
                snapshots = self.check_snapshots(project=project, cloud_account=cloud_account)
        else:
            snapshots = self.check_snapshots(project=project_id, cloud_account=cloud_account)

        for snapshot in snapshots:
            with OpenstackConnection(cloud_name=cloud_account) as conn:
                proj = conn.get_project(name_or_id=snapshot["project_id"])

            output["server_list"].append({
                "dataTitle":{
                    "name":proj["name"]
                },
                "dataBody":snapshot
            })
            #Send email to notify users? projects don't have contact details :/

            return output

    def check_snapshots(self, cloud_account, project: str):
        snap_list = []
        with OpenstackConnection(cloud_name=cloud_account) as conn:
            volume_snapshots = conn.list_volume_snapshots(search_opts={"all_tenants":True, "project_id": project})
        for snapshot in volume_snapshots:
            since_updated = datetime.strptime(snapshot["updated_at"], '%Y-%m-%dT%H:%M:%S.%f')
            if since_updated.month != datetime.now().month:
                snap_list.append({"name": snapshot["name"], "id": snapshot["id"], "updated": snapshot["updated_at"], "project_id": snapshot['os-extended-snapshot-attributes:project_id']})
        return snap_list


    def create_ticket(self, tickets_info, email: str, api_key: str, servicedesk_id, requesttype_id):
        """
        Function to create tickets in anatlassian project. The tickets_info value should be formatted as such:
        {
            "title": "This is the {p[title]}",
            "body": "This is the {p[body]}", #The {p[value]} is used by python formatting to insert the correct value in this spot, based off data passed in with server_list
            "server_list": [
                {
                    "dataTitle":{"title": "This replaces the {p[title]} value!"}, #These dictionary entries are picked up in create_ticket
                    "dataBody":{"body": "This replaces the {p[body]} value"}
                }
            ] This list can be arbitrarily long, it will be iterated and each element will create a ticket based off the title and body keys and modified with the info from dataTitle and dataBody. For an example on how to do this please see deleting_machines_check
        }
        """
        actual_tickets_info = tickets_info["result"]

        print("The tickets info is", actual_tickets_info)
        if len(actual_tickets_info["server_list"]) == 0:
            logging.info("No issues found")
            sys.exit()
        for i in actual_tickets_info["server_list"]:

            issue = requests.post("https://stfc.atlassian.net/rest/servicedeskapi/request",
            auth=HTTPBasicAuth(email,api_key),
            headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            },
            json={'requestFieldValues': {
                'summary': actual_tickets_info['title'].format(p = i['dataTitle']),
                'description': actual_tickets_info['body'].format(p = i["dataBody"]),
            },
            'serviceDeskId': servicedesk_id, #Point this at relevant service desk
            'requestTypeId': requesttype_id
            })

            if issue.status_code != 201:
                logging.error("Error creating issue issue", issue.status_code)
            else:
                logging.info("Created issue")
