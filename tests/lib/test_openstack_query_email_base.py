from typing import List
from unittest.mock import MagicMock

from nose.tools import raises

from openstack_api.openstack_query_email_base import OpenstackQueryEmailBase
from structs.email_params import EmailParams
from tests.lib.test_openstack_query_base import OpenstackQueryBaseTests


class OpenstackQueryEmailBaseTests(OpenstackQueryBaseTests):
    """
    Runs various tests to ensure OpenstackQueryEmailBase works correctly

    self.instance, search_query_presets and search_query_presets_no_project should be assigned in tests that inherit
    from this during the setUp method
    """

    instance: OpenstackQueryEmailBase
    search_query_presets: List[str]
    search_query_presets_no_project: List[str]

    @raises(ValueError)
    def test_email_users_no_email_error(self):
        """
        Tests the that email_users gives a value error when project_email is not present in the `properties_to_select`
        """
        smtp_account = MagicMock()
        email_params = EmailParams(
            subject="Subject",
            email_from="testemail",
            email_cc=[],
            header="",
            footer="",
            attachment_filepaths=[],
            test_override=False,
            test_override_email=[""],
            send_as_html=False,
        )
        self.instance.query_and_email_users(
            cloud_account="test_account",
            smtp_account=smtp_account,
            project_identifier="",
            query_preset=self.search_query_presets[0],
            message="Message",
            properties_to_select=["name"],
            email_params=email_params,
            days=60,
            ids=None,
            names=None,
            name_snippets=None,
        )

    @raises(ValueError)
    def test_email_users_invalid_query(self):
        """
        Tests the that email_users gives a value error when required_email_property is not present in the
        `properties_to_select`
        """
        smtp_account = MagicMock()
        email_params = EmailParams(
            subject="Subject",
            email_from="testemail",
            email_cc=[],
            header="",
            footer="",
            attachment_filepaths=[],
            test_override=False,
            test_override_email=[""],
            send_as_html=False,
        )
        self.instance.query_and_email_users(
            cloud_account="test_account",
            smtp_account=smtp_account,
            project_identifier="",
            query_preset="invalid_query",
            message="Message",
            # pylint:disable=protected-access
            properties_to_select=[
                self.instance._email_query_params.required_email_property
            ],
            email_params=email_params,
            days=60,
            ids=None,
            names=None,
            name_snippets=None,
        )

    def _email_users(self, query_preset: str):
        """
        Helper for checking email_users works correctly
        """
        smtp_account = MagicMock()
        email_params = EmailParams(
            subject="Subject",
            email_from="testemail",
            email_cc=[],
            header="",
            footer="",
            attachment_filepaths=[],
            test_override=False,
            test_override_email=[""],
            send_as_html=False,
        )
        return self.instance.query_and_email_users(
            cloud_account="test_account",
            smtp_account=smtp_account,
            project_identifier="",
            query_preset=query_preset,
            message="Message",
            # pylint:disable=protected-access
            properties_to_select=[
                self.instance._email_query_params.required_email_property
            ],
            email_params=email_params,
            days=60,
            ids=None,
            names=None,
            name_snippets=None,
        )

    def test_email_users_no_project(self):
        """
        Tests that email_users does not give a value error when a project is not required for the query type
        """

        for query_preset in self.search_query_presets_no_project:
            self._email_users(query_preset)

    @raises(ValueError)
    def _check_email_users_raises(self, query_preset):
        """
        Helper for checking email_users raises a ValueError when needed (needed to allow multiple to be checked
        in the same test otherwise it stops after the first error)
        """
        self._email_users(query_preset)

    def test_email_users_no_project_raises(self):
        """
        Tests that email_users gives a value error when a project is not required for the query type
        """

        # Should raise an error for all but servers_older_than and servers_last_updated_before
        should_pass = self.search_query_presets_no_project
        should_not_pass = [x for x in self.search_query_presets if x not in should_pass]

        for query_preset in should_not_pass:
            self._check_email_users_raises(query_preset)
