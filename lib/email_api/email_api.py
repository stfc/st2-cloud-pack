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
        :param: email_params: See EmailParams
        :param: email_to (List[String]): Email addresses to send the email to
        :param: body (String): body of email,
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """

        chosen_email_to = email_params.test_override_email

        if not email_params.test_override_email:
            chosen_email_to = (
                (email_to + email_params.email_cc)
                if email_params.email_cc
                else email_to
            )

        msg = MIMEMultipart()
        msg["Subject"] = Header(email_params.subject, "utf-8")
        msg["From"] = email_params.email_from
        msg["To"] = ", ".join(chosen_email_to)

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

        smtp.sendmail(email_params.email_from, email_to, msg.as_string())
        smtp.quit()
        return (True, "Email sent")

    def send_emails(
        self,
        smtp_account: SMTPAccount,
        emails: Dict[str, str],
        email_params: EmailParams,
    ):
        """
        Sends multiple emails
        :param: smtp_account (SMTPAccount): SMTP config
        :param: emails (Dict): Keys are email addresses, values are messages to send to those emails
        :param: email_params: See EmailParams
        :return: Status (Bool): tuple of action status (succeeded(T)/failed(F))
        """
        if email_params.test_override:
            # Send a maximum of 10 emails
            emails = dict(random.sample(emails.items(), min(len(emails), 10)))

        return all(
            [
                self.send_email(
                    smtp_account=smtp_account,
                    email_params=email_params,
                    email_to=[key],
                    body=value,
                )[0]
            ]
            for key, value in emails.items()
        )
