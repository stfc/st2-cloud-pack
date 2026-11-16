"""
Functions for building and sending emails via SMTP.

An email body is assembled by rendering and concatenating one or more named Jinja2 templates
HTML emails are wrapped in a template with custom inline CSS.

Typical usage::

    smtp = SMTPAccount(server="smtp.example.com", port=587, ...)
    templates = [
        EmailTemplateDetails("shutoff_vm", {"username": "alice", "shutoff_table": table}),
        EmailTemplateDetails("footer"),
    ]
    params = EmailParams(
        subject="Your VMs",
        email_from="cloud@example.com",
        email_to=["alice@example.com"],
        email_templates=templates,
        as_html=True,
    )
    send_emails(smtp, [params])
"""

import ssl
import time
import logging
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from smtplib import SMTP
from typing import List

# pylint:disable=no-name-in-module
from css_inline import CSSInliner

from apis.email_api.render_templates import render_html_template, render_plaintext_template
from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount

logger = logging.getLogger(__name__)

# Path to the directory where email attachment files are stored.
EMAIL_ATTACHMENTS_ROOT_DIR = (
    Path(__file__).resolve().parent.parent.parent / "email_attachments"
)


def _build_email(email_params: EmailParams) -> MIMEMultipart:
    """
    Create MIMEMultipart object ready to email.

    :params email_params: EmailParams dataclass - stores Addresses, subject, templates etc.
    :returns: A MIMEMultipart message with headers, body, and any attachments set.
    """
    msg = MIMEMultipart()
    msg["Subject"] = Header(email_params.subject, "utf-8")
    msg["From"] = email_params.email_from
    msg["To"] = ", ".join(email_params.email_to) if email_params.email_to else None
    msg["Cc"] = ", ".join(email_params.email_cc) if email_params.email_cc else None
    msg["Date"] = formatdate(localtime=True)
    msg["reply-to"] = email_params.email_from
    msg.attach(_build_email_body(email_params.email_templates, email_params.as_html))

    if email_params.attachment_filepaths:
        _attach_files(msg, email_params.attachment_filepaths)

    return msg


def _build_email_body(
    templates: List[EmailTemplateDetails], as_html: bool
) -> MIMEText:
    """
    Render and concatenate templates into a MIMEText email body.

    Each template in ``templates`` is rendered in order and the results
    are concatenated.

    For HTML emails the rendered body is wrapped in the shared
    ``wrapper`` layout template and custom inline CSS.

    :params templates: Ordered list of templates to render and concatenate.
    :params as_html: If True, render as HTML and inline CSS. Otherwise render as plaintext.
    :returns: A MIMEText object containing the complete rendered body.

    """
    render = render_html_template if as_html else render_plaintext_template
    body = "".join(render(t) for t in templates)

    if as_html:
        wrapper = EmailTemplateDetails(
            template_name="wrapper", template_params={"body": body}
        )
        html_body = render_html_template(wrapper)
        html_body = CSSInliner(keep_style_tags=True).inline(html_body)
        return MIMEText(html_body, "html")

    return MIMEText(body, "plain", "utf-8")


def _attach_files(msg: MIMEMultipart, filepaths: List[str]) -> None:
    """
    Load files from disk and attach them to an email message.

    :params msg: The MIMEMultipart message to attach files to. Modified in place.
    :params filepaths: Relative paths to attachment files, resolved from
        ``EMAIL_ATTACHMENTS_ROOT_DIR``.
    :raises RuntimeError: If any file in ``filepaths`` does not exist on disk.
    """
    logger.debug("attaching %s file(s) to email", len(filepaths))
    for rel_filepath in filepaths:
        filepath = EMAIL_ATTACHMENTS_ROOT_DIR / rel_filepath
        try:
            with open(filepath, "rb") as file:
                part = MIMEApplication(file.read(), Name=filepath.name)
            part["Content-Disposition"] = f"attachment; filename={filepath.name}"
            msg.attach(part)
            logger.debug("attached file - %s", filepath.name)
        except FileNotFoundError as exc:
            raise RuntimeError(f"Failed to attach file to email: {exc}") from exc


def send_email(smtp_account: SMTPAccount, email_params: EmailParams) -> None:
    """
    Send a single email via the configured SMTP relay.

    :params smtp_account: SMTP connection and credential config.
    :params email_params: Addressing, subject, templates and other email config.

    """
    logger.debug("connecting to SMTP server")
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with SMTP(smtp_account.server, smtp_account.port, timeout=60) as server:
        server.ehlo()
        server.starttls(context=context)
        logger.info("SMTP server connection established")
        logger.debug(
            "sending email:"
            "\n\tto: %s"
            "\n\tcc'd: %s"
            "\n\tfrom: %s"
            "\n\twith templates: %s\n",
            ", ".join(email_params.email_to),
            ", ".join(email_params.email_cc if email_params.email_cc else ["<none>"]),
            email_params.email_from,
            ", ".join(t.template_name for t in email_params.email_templates),
        )

        send_to = list(email_params.email_to)
        if email_params.email_cc:
            send_to.extend(email_params.email_cc)

        server.sendmail(
            email_params.email_from,
            tuple(send_to),
            _build_email(email_params).as_string(),
        )


def send_emails(smtp_account: SMTPAccount, emails: List[EmailParams]) -> None:
    """
    Send a list of emails via the configured SMTP relay.
    Calls send_email() for each `EmailParams` object in `emails` list

    :params smtp_account: SMTP connection and credential config.
    :params emails: List of email param configs to send, one per email.
    """
    logger.info("sending %s email(s)", len(emails))
    start = time.time()
    for email_params in emails:
        send_email(smtp_account, email_params)
    logger.info("sending complete - time elapsed: %s seconds", time.time() - start)
