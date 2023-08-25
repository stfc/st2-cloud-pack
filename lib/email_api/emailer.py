import time
from typing import List
from pathlib import Path
from smtplib import SMTP_SSL
import logging

from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from email_api.template_handler import TemplateHandler

from structs.email.email_params import EmailParams
from structs.email.smtp_account import SMTPAccount
from structs.email.email_template_details import EmailTemplateDetails

# pylint:disable=too-few-public-methods
logger = logging.getLogger(__name__)


class Emailer:
    """
    Emailer class is responsible for building and sending emails.
    """

    # Holds absolute dirpath to directory where email attachements files are stored
    EMAIL_ATTACHMENTS_ROOT_DIR = (
        Path(__file__).resolve().parent.parent.parent / "email_attachments"
    )

    def __init__(self, smtp_account: SMTPAccount, template_handler = TemplateHandler()):
        self._smtp_account = smtp_account
        self._template_handler = template_handler

    def send_emails(self, emails: List[EmailParams]):
        """
        send emails via SMTP server relay
        :param emails: A list of email param config objects
        """

        logger.debug("connecting to SMTP server")

        with SMTP_SSL(
            self._smtp_account.server, self._smtp_account.port, timeout=60
        ) as server:
            server.ehlo()
            logger.info("SMTP server connection established")
            logger.info("sending %s email(s)", len(emails))
            start = time.time()
            for email_params in emails:
                logger.debug(
                    "sending email: "
                    "\n\tto: %s"
                    "\n\tcc'd: %s"
                    "\n\tfrom: %s"
                    "\n\twith templates: %s\n",
                    ", ".join(email_params.email_to),
                    ", ".join(
                        email_params.email_cc if email_params.email_cc else ["<none>"]
                    ),
                    email_params.email_from,
                    ", ".join(
                        [f"{tmp.template_name}" for tmp in email_params.email_templates]
                    ),
                )

                send_to = email_params.email_to
                if email_params.email_cc:
                    send_to += email_params.email_cc

                server.sendmail(
                    email_params.email_from,
                    send_to,
                    self.build_email_header(email_params).as_string(),
                )

            logger.info(
                "sending complete - time elapsed: %s seconds", time.time() - start
            )

    def build_email_header(self, email_params: EmailParams) -> MIMEMultipart:
        """
        Helper function to setup email as MIMEMultipart
        :param email_params: A dataclass holding parameters for building an email
        """
        msg = MIMEMultipart()
        msg["Subject"] = Header(email_params.subject, "utf-8")
        msg["From"] = email_params.email_from
        msg["To"] = ", ".join(email_params.email_to) if email_params.email_to else None
        msg["Cc"] = ", ".join(email_params.email_cc) if email_params.email_cc else None
        msg["Date"] = formatdate(localtime=True)
        msg["reply-to"] = email_params.email_from
        msg.attach(
            self.build_email_body(email_params.email_templates, email_params.as_html)
        )
        if email_params.attachment_filepaths:
            msg = self._attach_files(msg, email_params.attachment_filepaths)
        return msg

    def build_email_body(self, templates: List[EmailTemplateDetails], as_html):
        """
        Helper function to setup email body from templates
        :param templates: A list of dataclasses holding template information to build emails from
        """
        msg_body = ""
        for template_details in templates:
            if as_html:
                msg_body += self._template_handler.render_html_template(
                    template_details
                )
            else:
                msg_body += self._template_handler.render_plaintext_template(
                    template_details
                )

        if as_html:
            return MIMEText(msg_body, "html")
        return MIMEText(msg_body, "plain", "utf-8")

    def _attach_files(self, msg: MIMEMultipart, filepaths: List[str]) -> MIMEMultipart:
        """
        Loads and adds attachments to an email message
        :param msg: The message object for the email
        :param filepaths: Tuple containing relative filepaths of files to attach from EMAIL_ATTACHMENTS_ROOT_DIR
        """
        logger.debug("attaching %s file(s) to email", len(filepaths))
        for rel_filepath in filepaths:
            filepath = self.EMAIL_ATTACHMENTS_ROOT_DIR / rel_filepath
            try:
                with open(filepath, "rb") as file:
                    part = MIMEApplication(file.read(), Name=filepath.name)
                part["Content-Disposition"] = f"attachment; filename={filepath.name}"
                msg.attach(part)
                logger.debug("attached file - %s", filepath.name)
            except FileNotFoundError as exp:
                raise RuntimeError(f"Failed to attach file to email: {exp}") from exp
        return msg
