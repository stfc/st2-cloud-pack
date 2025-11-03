from openstackquery import UserQuery


def find_user_info(user_id, cloud_account, override_email_address):
    """
    Run a UserQuery to find the email address and user name associated with the specified user ID.
    :param user_id: The OpenStack user ID to be queried
    :param cloud_account: String representing the cloud account to use
    :param override_email_address: String email address to return if no email address is found
    """
    user_query = UserQuery()
    user_query.select("name", "email_address")
    user_query.where("equal_to", "id", value=user_id)
    user_query.run(cloud_account=cloud_account)
    res = user_query.to_props(flatten=True)

    if not res or not res["user_email"][0]:
        return "", override_email_address

    return res["user_name"][0], res["user_email"][0]
