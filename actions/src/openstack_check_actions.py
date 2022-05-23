from cmath import sin
from typing import Dict, Callable
from openstack_api.openstack_connection import OpenstackConnection
from openstack_action import OpenstackAction
import json, time, os
from datetime import datetime
import requests, logging
from requests.auth import HTTPBasicAuth
from requests.auth import AuthBase

class TokenAuth(AuthBase):
    """Attaches token authentication to Request object"""
    def __init__(self, token) -> None:
        self.token = token

    def __call__(self, r):
        #Adds token to header
        r.headers['X-Auth-Token'] = self.token
        return r

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


    def checkProject(self, project: str, cloud: str, max_port: int, min_port: int, ip_prefix: str):
        rulesWithIssues = []

        with OpenstackConnection(cloud_name=cloud) as conn:
            sec_group = conn.list_security_groups(filters={"project_id":project})
        for group in sec_group:
                for rules in group["security_group_rules"]:

                    if rules["remote_ip_prefix"] == ip_prefix and rules["port_range_max"] == max_port and rules["port_range_min"] == min_port:
                        ruledict = {}
                        print("Issue with rule "+rules["security_group_id"])
                        ruledict["id"] = rules["security_group_id"]
                        ruledict["serverList"] =[]

                        with OpenstackConnection(cloud_name=cloud) as conn:
                            servers = conn.list_servers(filters={"all_tenants":True, "project_id": project}) #Using the inbuilt all_projects variable throws a connection issue, may have to change to projects in a future cloud upgrade

                        for server in servers:

                            with OpenstackConnection(cloud_name=cloud) as conn:
                                applied = conn.list_server_security_groups(server.id)

                            for serv_groups in applied:

                                if serv_groups.id == rules["security_group_id"]:
                                    print("Rule is applied")
                                    ruledict["serverList"].append(serv_groups.id)
                                else:
                                    print("Rule not applied to "+server.id)
                        rulesWithIssues.append(ruledict)
        return rulesWithIssues

    def security_groups_check(self, cloud_account: str, max_port: int, min_port: int, ip_prefix: str, project=None, all_projects=False):
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
        rulesWithIssues = []

        if all_projects:
            with OpenstackConnection(cloud_name=cloud_account) as conn:
                projects = conn.list_projects()
            for project in projects:
                output = self.checkProject(project=project, cloud=cloud_account, max_port=max_port, min_port=min_port, ip_prefix=ip_prefix)
                rulesWithIssues.append(output)
        else:
            
            output = self.checkProject(project=project, cloud=cloud_account, max_port=max_port, min_port=min_port, ip_prefix=ip_prefix)
            rulesWithIssues.append(output)
        return rulesWithIssues

    def deleting_machines_check(self, cloud_account: str, project=None, all_projects=False):
        output = {
            "title": "Server {p[id]} has not been updated in more than 10 minutes during {p[action]}",
            "body": "The following information may be useful\nHost id: {p[id]} \n{p[data]}",
            "serverList": []
        }

        if all_projects:
            with OpenstackConnection(cloud_name=cloud_account) as conn:
                projects = conn.list_projects()
            for project in projects:
                deleted = self.check_deleted(project=project, cloud=cloud_account)
            output["serverList"] = deleted
        else:
            
            deleted = self.check_deleted(project=project, cloud=cloud_account)
            output["serverList"] = deleted
        
        return output
        
    def check_deleted(cloud: str, project: str):
        output = []
        with OpenstackConnection(cloud_name=cloud) as conn:
            serverList = conn.list_servers(filters={"all_tenants":True, "project_id": project})
        #Loop through each server in the project/list
        for i in serverList:
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
            amphorae = requests.get("https://openstack.nubes.rl.ac.uk:9876/v2/octavia/amphorae", auth=TokenAuth(token=conn.auth_token))  

        try:
            amph_json = amphorae.json()
            
        except requests.exceptions.JSONDecodeError:
            logging.critical(msg="There was no JSON response \nThe status code was: "+str(amphorae.status_code)+"\nThe body was: \n"+str(amphorae.content))
            return "There was no JSON response \nThe status code was: "+str(amphorae.status_code)+"\nThe body was: \n"+str(amphorae.content)
        output = {
            "title": "{p[title_text]}",
            "body": "The loadbalance ping test result was: {p[lb_status]}\nThe status of the amphora was: {p[amp_status]}\nThe amphora id is: {p[amp_id]}\nThe loadbalancer id is: {p[lb_id]}",
            "serverList": []
        }
        if amphorae.status_code == 403:
            #Checks user has permissions to access api
            logging.critical("Please run this script using a cloud admin account.")
            return "Please run this script using a cloud admin account."
        elif amphorae.status_code == 200:
            #Gets list of amphorae and iterates through it to check the loadbalancer and amphora status.
            for i in amph_json["amphorae"]:
                with open("iamp.json", "w+") as f:
                    f.write(str(i))
                
                status = self.checkStatus(i)
                ping_result = self.pingLB(i['lb_network_ip'], status[1])
                
                if status[0] == 'error' or ping_result == 'error':
                    if status[0].lower() == 'error' and ping_result.lower() == 'error':
                        output["serverList"].append({
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
                        })
                    elif status[0].lower() == 'error':
                        output["serverList"].append({
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
                        })
                    elif ping_result.lower() == 'error':
                        output["serverList"].append({
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
                        })
                else:
                    logging.info(i['id']+" is fine.")
            
        else:
            #Notes problem with accessing api if anything other than 403 or 200 returned
            logging.critical("We encountered a problem accessing the API")
            logging.critical("The status code was: "+str(amphorae.status_code))
            logging.critical("The JSON response was: \n"+str(amph_json))
            exit()
        return output

    def checkStatus(self, amphora):
        #Extracts the status of the amphora and returns relevant info
        status = amphora['status']
        if status == 'ALLOCATED' or status == 'BOOTING' or status == 'READY':
            return ['ok', status]
        else:
            return ['error', status]    
    
    def pingLB(self, ip, status):
    #Runs the ping command to check that loadbalancer is up
        response = os.system("ping -c 1 "+ip) #Might want to update to subprocess as this has been deprecated

        #Checks output of ping command
        if response == 0:
            logging.info(msg="Successfully pinged " + ip)
            return 'success'
        else:
            logging.info(msg=ip + " is down")
            return 'error'


    def createTicket(self, tickets_info: Dict, email: str, api_key: str, serviceDeskId, requestTypeId):
        """
        Function to create tickets in anatlassian project. The tickets_info value should be formatted as such:
        {
            "title": "This is the {p[title]}",
            "body": "This is the {p[body]}", #The {p[value]} is used by python formatting to insert the correct value in this spot, based off data passed in with serverList
            "serverList": [
                {
                    "dataTitle":{"title": "This replaces the {p[title]} value!"}, #These dictionary entries are picked up in createTicket
                    "dataBody":{"body": "This replaces the {p[body]} value"}
                }
            ] #This list can be arbitrarily long, it will be iterated and each element will create a ticket based off the title and body keys and modified with the info from dataTitle and dataBody. For an example on how to do this please see deleting_machines_check
        }
        """

        for i in tickets_info["serverList"]:
            #print(str(i))
            issue = requests.post("https://stfc.atlassian.net/rest/servicedeskapi/request", 
            auth=HTTPBasicAuth(email,api_key),
            headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            }, 
            json={'requestFieldValues': {
                'summary': tickets_info['title'].format(p = i['dataTitle']),
                'description': tickets_info['body'].format(p = i["dataBody"]),
            }, 
            'serviceDeskId': serviceDeskId, #Point this at relevant service desk
            'requestTypeId':requestTypeId
            } #Create more descriptive request type for this
            
            ) 
            print(issue.status_code)
            if issue.status_code != 201:
                #print(str(issue.content))
                logging.info("Error creating issue issue")
                #return ['Error creating issue: '+str(issue.status_code), True]
            else:
                logging.error("Created issue")
                #return ['Created issue', False]


