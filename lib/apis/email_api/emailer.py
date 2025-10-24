import logging
import ssl
import time
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from smtplib import SMTP
from typing import List

from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount
from apis.email_api.template_handler import TemplateHandler

# weird issue where pylint can't find the module - works fine though
# pylint:disable=no-name-in-module
from css_inline import CSSInliner

logger = logging.getLogger(__name__)


class Emailer:
    """
    Emailer class is responsible for building and sending emails.
    """

    # Holds absolute dirpath to directory where email attachements files are stored
    EMAIL_ATTACHMENTS_ROOT_DIR = (
        Path(__file__).resolve().parent.parent.parent / "email_attachments"
    )

    def __init__(self, smtp_account: SMTPAccount, template_handler=TemplateHandler()):
        self.smtp_account = smtp_account
        self._template_handler = template_handler

    def send_email(self, email_params: EmailParams):
        """Send a single email via the configured SMTP relay."""

        logger.debug("connecting to SMTP server")
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with SMTP(
            self.smtp_account.server, self.smtp_account.port, timeout=60
        ) as server:
            server.ehlo()
            server.starttls(context=context)
            logger.info("SMTP server connection established")
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

            send_to = list(email_params.email_to)
            if email_params.email_cc:
                send_to.extend(email_params.email_cc)

            server.sendmail(
                email_params.email_from,
                tuple(send_to),
                self.build_email(email_params).as_string(),
            )

    def send_emails(self, emails: List[EmailParams]):
        """
        send emails via SMTP server relay
        :param emails: A list of email param config objects
        """

        logger.info("sending %s email(s)", len(emails))
        start = time.time()
        for email_params in emails:
            self.send_email(email_params)

        logger.info("sending complete - time elapsed: %s seconds", time.time() - start)

    def print_email(self, email_params: EmailParams):
        """
        Print a well-formatted version of the email that would be sent.
        Useful for debugging or dry-run previews.
        """
        # Build the MIME email using the same function that send_email uses
        msg = self.build_email(email_params)

        # Display email headers
        print("===== EMAIL PREVIEW =====")
        print(f"From   : {msg['From']}")
        print(f"To     : {msg['To']}")
        print(f"Cc     : {msg['Cc'] or '<none>'}")
        print(f"Subject: {msg['Subject']}")
        print(f"Date   : {msg['Date']}")
        print(f"Reply-To: {msg['reply-to']}")
        print("\n--- Body ---")

        # Extract and print the body parts (could be plain or HTML)
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = part.get("Content-Disposition", "").lower()
            if (
                content_type.startswith("text/")
                and "attachment" not in content_disposition
            ):
                charset = part.get_content_charset() or "utf-8"
                body = part.get_payload(decode=True).decode(charset, errors="replace")
                print(body)
                print("\n--- End of Body ---\n")

        # List any attachments
        attachments = []
        for part in msg.walk():
            content_disposition = part.get("Content-Disposition", "").lower()
            if "attachment" in content_disposition:
                filename = part.get_filename()
                attachments.append(filename)

        if attachments:
            print("--- Attachments ---")
            for filename in attachments:
                print(f"- {filename}")
        else:
            print("No attachments.")

        print("=========================\n")

    def build_email(self, email_params: EmailParams) -> MIMEMultipart:
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
            msg = self.attach_files(msg, email_params.attachment_filepaths)
        return msg

    def build_email_body(self, templates: List[EmailTemplateDetails], as_html):
        """
        Helper function to setup email body from templates
        :param templates: A list of dataclasses holding template information to build emails from
        :param as_html: whether the templates are to be rendered as HTML (True) or plaintext (False)
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
            # wrap the email in our own styling
            wrapper_template = EmailTemplateDetails(
                template_name="wrapper", template_params={"body": msg_body}
            )
            html_body = self._template_handler.render_html_template(wrapper_template)

            # convert style tags to inline styles for emails
            inliner = CSSInliner(keep_style_tags=True)
            html_body = inliner.inline(html_body)
            return MIMEText(html_body, "html")
        return MIMEText(msg_body, "plain", "utf-8")

    def attach_files(self, msg: MIMEMultipart, filepaths: List[str]) -> MIMEMultipart:
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
