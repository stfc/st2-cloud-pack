from typing import Dict
from apis.jira_api.issue_types.issue_base import IssueBase


class NewProjectRequestIssue(IssueBase):  # pylint: disable=too-few-public-methods
    """Issue class to handle new project requests"""

    def _create_properties(self) -> Dict:
        proforma_form = next(
            prop
            for prop in self.conn.issue_properties(self.issue_key)
            if prop.key == "proforma.forms.i1"
        )
        answers = proforma_form.value.state.answers

        return {
            "project_name": self._get_text(answers, "3"),
            "users": self._get_adf_text(answers, "29"),
            "cpus": self._get_int(answers, "32"),
            "vms": self._get_int(answers, "45"),
            "memory": self._get_int(answers, "33"),
            "shared_storage": self._get_int(answers, "34"),
            "object_storage": self._get_int(answers, "35"),
            "block_storage": self._get_int(answers, "44"),
            "gpus": self._get_adf_text(answers, "17"),
            "contact_email": self._get_text(answers, "25"),
            "reporting_fed_id": self._get_text(answers, "42"),
            "externally_accessible": self._get_choice(answers, "31") == "1",
            "tos_agreement": True,  # always true if form is submitted
        }
