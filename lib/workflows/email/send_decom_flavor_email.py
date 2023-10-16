from typing import List, Optional

from openstack_query import FlavorQuery, UserQuery
from enums.query.props.flavor_properties import FlavorProperties
from enums.query.props.server_properties import ServerProperties
from enums.query.props.project_properties import ProjectProperties
from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import QueryPresetsGeneric
from structs.email.smtp_account import SMTPAccount
from structs.email.email_template_details import EmailTemplateDetails
from structs.email.email_params import EmailParams
from email_api.emailer import Emailer
from tabulate import tabulate


def send_decom_flavor_email(
    smtp_account: SMTPAccount,
    cloud_account: str,
    decom_flavor_list: List[str],
    project_list: Optional[List[str]] = None,
    all_projects: bool = False,
    send_email: bool = False,
    as_html: bool = False,
    **kwargs,
):
    """
    Sends an email to each user who owns one or more VMs that have a flavor that is to be decommissioned.
    This email will contain a notice to delete or rebuild the VM
    :param smtp_account: (SMTPAccount): SMTP config
    :param cloud_account: string represents cloud account to use
    :param decom_flavor_list: A list of flavor names to be decommissioned
    :param project_list: A list of projects to limit search in
    :param all_projects: A boolean which if selected will search in all projects
    :param send_email: Actually send the email instead of printing what will be sent
    :param as_html: Send email as html
    :param kwargs: see EmailParams dataclass class docstring
    """

    if project_list and all_projects:
        raise RuntimeError(
            "given both project list and all_projects flag - please choose only one"
        )

    # flavor query
    q1 = FlavorQuery().where(
        QueryPresetsGeneric.EQUAL_TO, FlavorProperties.FLAVOR_IS_PUBLIC, value=True
    )
    q1.where(
        QueryPresetsGeneric.ANY_IN,
        FlavorProperties.FLAVOR_NAME,
        values=decom_flavor_list,
    )
    q1.run(cloud_account)
    q1.sort_by((FlavorProperties.FLAVOR_ID, False))

    # server query
    q2 = q1.then(query_type="SERVER_QUERY", forward_outputs=True).run(
        cloud_account, as_admin=True, all_projects=True
    )
    q2.append_from("PROJECT_QUERY", cloud_account, ProjectProperties.PROJECT_NAME)
    q2.select(
        ServerProperties.SERVER_ID,
        ServerProperties.SERVER_NAME,
        ServerProperties.ADDRESSES,
    )

    # user query
    q3 = q2.then("USER_QUERY", forward_outputs=True).run(cloud_account)
    q3.select(UserProperties.USER_NAME)
    q3.group_by(UserProperties.USER_EMAIL)
    decom_results = q3.to_list()

    for email_addr, outputs in decom_results.items():
        user_name = outputs[0]["user_name"]
        for output in outputs:
            del output["user_name"]

        flavor_list = [["Flavor Name"]]
        flavor_list.extend([[flavor] for flavor in decom_flavor_list])
        flavor_table = tabulate(flavor_list)

        if not send_email:
            print(f"Send Email To: {email_addr}")
            print(f"email_templates decom-email: username {user_name}")
            print(f"send as html: {as_html}")
            print(f"flavor table: {flavor_table}")
            print(f"decom table: {q3.to_string(groups=[email_addr])}")
            print("\n\n")
            break

        email_params = EmailParams.from_dict(
            {
                **{
                    "email_templates": [
                        EmailTemplateDetails(
                            template_name="decom_email",
                            template_params={
                                "username": user_name,
                                "affected_flavors_table": flavor_table,
                                "decom_table": q3.to_string(groups=[email_addr]),
                            },
                        ),
                        EmailTemplateDetails(
                            template_name="footer", template_params={}
                        ),
                    ],
                    "email_to": email_addr,
                    "as_html": as_html,
                },
                **kwargs,
            }
        )
        # TODO uncomment this to actually send emails
        # Emailer(smtp_account).send_emails([email_params])


# TODO - need to remove this and add stackstorm action
if __name__ == "__main__":
    send_decom_flavor_email(
        None,
        "prod",
        [
            "c1.xlarge",
            "c3.small",
            "c2.large",
            "c1.xxlarge",
            "c3.xlarge",
            "c1.3xl",
            "c3.medium",
            "c3.large",
            "c1.medium",
            "c1.large",
            "c2.xlarge",
            "c2.medium",
            "c1.5xl",
            "c1.4xl",
        ],
        project_list=None,
        all_projects=True,
        send_email=False,
    )
