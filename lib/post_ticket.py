import requests
from requests.auth import HTTPBasicAuth


def post_ticket(
    tickets_info, ticket_details, service_desk_id, request_type_id, email, api_key
):
    """
    Returns a requests that has created a ticket in atlassian
    :param dict tickets_info: Basic data that is needed to create the ticket
    :param str service_desk_id: The service desk to send the ticket to
    :param str request_type_id: The type of ticket to create
    """

    return requests.post(
        "https://stfc.atlassian.net/rest/servicedeskapi/request",
        auth=HTTPBasicAuth(email, api_key),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={
            "requestFieldValues": {
                "summary": tickets_info["title"].format(p=ticket_details["dataTitle"]),
                "description": tickets_info["body"].format(
                    p=ticket_details["dataBody"]
                ),
            },
            "serviceDeskId": service_desk_id,  # Point this at relevant service desk
            "requestTypeId": request_type_id,
        },
    )
