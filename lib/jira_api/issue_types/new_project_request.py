from typing import Dict
from issue_base import IssueBase


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

        properties["project_name"] = getattr(answers, "1").text
        properties["users"] = getattr(answers, "4").adf.content[0].content[0].text
        properties["cpus"] = int(getattr(answers, "6").text)
        properties["memory"] = int(getattr(answers, "7").text)
        properties["shared_storage"] = int(getattr(answers, "9").text)
        properties["object_storage"] = getattr(answers, "10").text
        properties["gpus"] = getattr(answers, "11").adf.content[0].content[0].text
        properties["contact_email"] = getattr(answers, "12").text
        properties["tos_agreement"] = getattr(answers, "12").text
        properties["project_name"] = getattr(answers, "13").text

        if getattr(answers, "5").choices[0] == "1":
            properties["externally_accessible"] = True
        elif getattr(answers, "5").choices[0] == "2":
            properties["externally_accessible"] = False
        else:
            self.reply(
                "Choice made for external networking is not correct. Please check this.",
                True,
            )
            raise RuntimeError("Some error.")

        return properties
