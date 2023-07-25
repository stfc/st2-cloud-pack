import os
from typing import Tuple, Dict, List, Optional
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from structs.email_params import EmailParams
from structs.smtp_account import SMTPAccount


class Emailer:
    """
    Emailer class is responsible for building and sending emails.
    """

    # Holds absolute dirpath to directory where email attachements files are stored
    EMAIL_ATTACHMENTS_ROOT_DIR = os.path.normpath(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "../email_attachments"
        )
    )

    def __init__(self, smtp_account: SMTPAccount):
        self._smtp_account = smtp_account

    def send_multiple_emails(
        self, emails: Dict[Tuple[str], EmailParams], as_html: bool = True
    ):
        """
        send multiple emails
        :param emails: (Dict) keys are list of email addresses, values are configured EmailParams dataclass
        :param as_html: whether to send emails using html message body (if True), or plaintext (if False) (Default True)
        """
        for email_to, email_params in emails.items():
            self.send_email(email_to, email_params, as_html)

    def send_email(
        self, email_to: Tuple[str], email_params: EmailParams, as_html: bool = True
    ):
        """
        send a single email
        :param email_params: An EmailParams Dataclass which holds all config info needed to build and send an email
        :param email_to: email addresses to send the email to
        :param as_html: whether to send email using html message body (if True), or plaintext (if False) (Default True)

        """
        msg = Emailer._build_message(email_params, email_to, as_html)
        with SMTP_SSL(
            self._smtp_account.server, self._smtp_account.port, timeout=60
        ) as server:
            server = Emailer._setup_smtp(server, self._smtp_account)
            server.sendmail(email_params.email_from, email_to, msg.as_string())

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
    def _build_message(
        email_params: EmailParams, email_to: Tuple[str], as_html: bool = True
    ):
        """
        build message object for a single email
        :param email_params: An EmailParams Dataclass which holds all config info needed to build and send an email
        :param: email_to: Email addresses to send the email to
        :param as_html: whether to build email message as html (if True), or plaintext (if False) (Default True)
        """

        msg = Emailer._setup_email_metadata(
            email_to, email_params.email_from, email_params.subject
        )

        if as_html:
            msg.attach(MIMEText(email_params.body_html, "html"))
        else:
            msg.attach(MIMEText(email_params.body_plaintext, "plain", "utf-8"))

        if email_params.attachment_filepaths:
            msg = Emailer._attach_files(msg, email_params.attachment_filepaths)
        return msg

    @staticmethod
    def _setup_email_metadata(
        email_to: Tuple[str],
        email_from: str,
        subject: str,
        email_cc: Optional[Tuple[str]] = None,
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
        if email_cc:
            msg["Cc"] = ", ".join(email_cc)
        return msg

    @staticmethod
    def _attach_files(msg: MIMEMultipart, filepaths: List[str]) -> MIMEMultipart:
        """
        Loads and adds attachments to an email message
        :param msg: The message object for the email
        :param filepaths: Tuple containing relative filepaths of files to attach from EMAIL_ATTACHMENTS_ROOT_DIR
        """
        for rel_filepath in filepaths:
            filename = os.path.basename(rel_filepath)
            try:
                with open(
                    os.path.normpath(
                        os.path.join(Emailer.EMAIL_ATTACHMENTS_ROOT_DIR, rel_filepath)
                    ),
                    "rb",
                ) as file:
                    part = MIMEApplication(file.read(), Name=filename)
                part["Content-Disposition"] = f"attachment; filename={filename}"
                msg.attach(part)
            except FileNotFoundError as exp:
                raise RuntimeError(f"Failed to attach file to email: {exp}") from exp
        return msg
