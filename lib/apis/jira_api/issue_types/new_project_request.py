from typing import Dict
from apis.jira_api.issue_types.issue_base import IssueBase


class NewProjectRequestIssue(IssueBase):  # pylint: disable=too-few-public-methods
    """Issue class to handle new project requests"""

    def _create_properties(self) -> Dict:
        properties = {}
        proforma_form = [
            prop
            for prop in self.conn.issue_properties(self.issue_key)
            if prop.key == "proforma.forms.i1"
        ][0]
        answers = proforma_form.value.state.answers

        properties["project_name"] = getattr(answers, "3").text
        potential_users_info = getattr(answers, "29").adf.content
        if potential_users_info:
            # the value is not an empty string
            properties["users"] = potential_users_info[0].content[0].text
        else:
            properties["users"] = ""
        properties["cpus"] = int(getattr(answers, "32").text)
        properties["vms"] = int(getattr(answers, "45").text)
        properties["memory"] = int(getattr(answers, "33").text)
        properties["shared_storage"] = int(getattr(answers, "34").text)
        properties["object_storage"] = int(getattr(answers, "35").text)
        properties["block_storage"] = int(getattr(answers, "44").text)
        potential_gpus_info = getattr(answers, "17").adf.content
        if potential_gpus_info:
            # the value is not an empty string
            properties["gpus"] = potential_gpus_info[0].content[0].text
        else:
            properties["gpus"] = ""
        properties["contact_email"] = getattr(answers, "25").text
        properties["reporting_fed_id"] = getattr(answers, "42").text

        if getattr(answers, "31").choices[0] == "1":
            properties["externally_accessible"] = True
        else:
            properties["externally_accessible"] = False

        # This can only be true otherwise the form cannot be submitted
        properties["tos_agreement"] = True

        return properties
