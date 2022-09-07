import os
import random
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Dict, List

from email_api.prep_html import prep_html
from structs.email_params import EmailParams
from structs.smtp_account import SMTPAccount


class EmailApi:
    def load_template(self, path):
        """
        Loads and returns a html template from its path
        :param path: File path of the template
        :return: (String) The contents of the file in utf-8 format
        """
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as header_file:
                return header_file.read()
        else:
            raise FileNotFoundError(f"Template file located {path} not found")

    def attach_files(self, msg: MIMEMultipart, files) -> MIMEMultipart:
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

    # pylint:disable=too-many-arguments
    def send_email(
        self,
        smtp_account: SMTPAccount,
        email_params: EmailParams,
        email_to: List[str],
        body: str,
    ):
        """
        Send an email
        :param: smtp_account (SMTPAccount): SMTP config
        :param: subject: (String): Subject of the email
        :param: email_to (List[String]): Email addresses to send the email to
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: header (String): filepath to header file,
        :param: footer (String): filepath to footer file,
        :param: body (String): body of email,
        :param: attachment_filepaths (List): list of attachment filepaths,
        :param: send_as_html (Bool): If true will send in HTML format
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """

        msg = MIMEMultipart()
        msg["Subject"] = Header(email_params.subject, "utf-8")
        msg["From"] = email_params.email_from
        msg["To"] = ", ".join(email_to)

        msg["Date"] = formatdate(localtime=True)

        header = self.load_template(email_params.header)
        footer = self.load_template(email_params.footer)

        if email_params.send_as_html:
            msg.attach(
                MIMEText(
                    prep_html(header=header, body=body, footer=footer),
                    "html",
                )
            )
        else:
            msg.attach(MIMEText(f"{header}\n{body}\n{footer}", "plain", "utf-8"))

        if email_params.email_cc:
            msg["Cc"] = ", ".join(email_params.email_cc)

        if (
            email_params.attachment_filepaths
            and len(email_params.attachment_filepaths) > 0
        ):
            msg = self.attach_files(msg, email_params.attachment_filepaths)

        smtp = SMTP_SSL(smtp_account.server, smtp_account.port, timeout=60)
        smtp.ehlo()

        if smtp_account.secure:
            smtp.starttls()
        if smtp_account.smtp_auth:
            smtp.login(smtp_account.username, smtp_account.password)

        email_to = (
            (email_to + email_params.email_cc) if email_params.email_cc else email_to
        )

        smtp.sendmail(email_params.email_from, email_to, msg.as_string())
        smtp.quit()
        return (True, "Email sent")

    # pylint:disable=too-many-arguments
    def send_emails(
        self,
        smtp_account: SMTPAccount,
        emails: Dict[str, str],
        email_params: EmailParams,
    ):
        """
        Sends multiple emails
        :param: smtp_account (SMTPAccount): SMTP config
        :emails (Dict): Keys are email addresses, values are messages to send to those emails
        :param: subject: (String): Subject of the email
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: header (String): filepath to header file,
        :param: footer (String): filepath to footer file,
        :param: attachment (List): list of attachment filepaths,
        :param: test_override (Boolean): send all emails to test emails
        :param: test_override_email (List[String]): send to this email if test_override enabled
        :param: send_as_html (Bool): If true will send in HTML format
        :return: Status (Bool): tuple of action status (succeeded(T)/failed(F))
        """
        if email_params.test_override:
            # Send a maximum of 10 emails
            emails = dict(random.sample(emails.items(), min(len(emails), 10)))
            override_email = email_params.test_override_email

        return all(
            [
                self.send_email(
                    smtp_account=smtp_account,
                    email_params=email_params,
                    email_to=override_email if email_params.test_override else [key],
                    body=value,
                )[0]
            ]
            for key, value in emails.items()
        )
