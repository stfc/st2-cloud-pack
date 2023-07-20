import os
from typing import List, Dict
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from email_api.template_hanlder import TemplateHandler
from structs.email_params import EmailParams
from structs.smtp_account import SMTPAccount


class Emailer:
    """
    Emailer class is responsible for building and sending emails. Public methods can be used by EmailActions to send
    emails
    """

    def __init__(self, smtp_account: SMTPAccount):
        self._smtp_account = smtp_account

    def send_emails(
        self,
        emails: Dict[List[str], EmailParams],
    ):
        """
        send emails
        :param emails: (Dict) keys are list of email addresses, values are configured EmailParams dataclass
        """
        for email_to, email_params in emails.items():
            self.send_email(email_to, email_params)

    def send_email(
        self,
        email_to: List[str],
        email_params: EmailParams,
    ):
        """
        send an email
        :param email_params: An EmailParams Dataclass which holds all config info needed to build and send an email
        :param email_to: email addresses to send the email to
        """
        msg = Emailer._build_messsage(email_params, email_to)
        with SMTP_SSL(
            self._smtp_account.server, self._smtp_account.port, timeout=60
        ) as server:
            server = Emailer._setup_smtp(server, self._smtp_account)
            server.sendmail(msg["From"], msg["To"], msg.as_string())

    @staticmethod
    def _setup_smtp(server, smtp_account):
        """
        setup SMTP
        :param smtp_account: SMTP config
        """
        server.ehlo()
        if smtp_account.secure:
            server.starttls()
        if smtp_account.smtp_auth:
            server.login(smtp_account.username, smtp_account.password)
        return server

    @staticmethod
    def _build_messsage(
        email_params: EmailParams,
        email_to: List[str],
    ):
        """
        build message object for a single email
        :param email_params: An EmailParams Dataclass which holds all config info needed to build and send an email
        :param: email_to: Email addresses to send the email to
        """

        chosen_email_to = (
            email_params.test_override_email
            if email_params.test_override_email
            else email_to
        )
        msg = Emailer._setup_email_metadata(
            chosen_email_to, email_params.email_from, email_params.subject
        )
        msg.attach(
            Emailer._setup_email_body(email_params.body_html, True)
        ) if email_params.send_as_html else msg.attach(
            self._setup_email_body(email_params.body_plaintext, False)
        )
        msg = Emailer._attach_files(msg, email_params.attachment_filepaths)
        return msg

    @staticmethod
    def _setup_email_metadata(
        email_to: List[str], email_from: str, subject: str, email_cc: List[str] = None
    ):
        """
        Setup message object metadata
        :param email_to: List of email addresses to send email to
        :param email_from: email address to send email from
        :param subject: email subject
        :param email_cc: email addresses to cc into email
        """
        msg = MIMEMultipart()
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = email_from
        msg["To"] = ", ".join(email_to)
        msg["Date"] = formatdate(localtime=True)
        msg["Cc"] = ", ".join(email_cc)
        return msg

    @staticmethod
    def _setup_email_body(body: str, is_html: bool):
        """
        Setup email message body
        :param body: a string which should be written in as email body (either HTML or plaintext)
        :param is_html: a flag to set string type - either html if True, plaintext if False
        """
        if is_html:
            email_body_html = TemplateHandler().render_template(
                template_name="wrapper",
                render_html=True,
                template_params={"body": body},
            )
            return MIMEText(email_body_html, "html")
        return MIMEText(body, "plain", "utf-8")

    @staticmethod
    def _attach_files(msg: MIMEMultipart, files) -> MIMEMultipart:
        """
        Loads and adds attachments to an email message
        :param msg: The message object for the email
        :param files: List/Tuple of file paths of files to attach
        :return:
        """
        for filepath in files:
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as file:
                part = MIMEApplication(file.read(), Name=filename)
            part["Content-Disposition"] = f"attachment; filename={filename}"
            msg.attach(part)
        return msg
