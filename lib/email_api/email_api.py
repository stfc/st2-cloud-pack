import os
import random
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Dict, List


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

    def load_smtp_account(self, pack_config: Dict, smtp_account: str):
        """
        Loads and returns the smtp account data from the pack config
        :param pack_config: The config for the pack
        :return: (Dictionary) SMTP account properties
        """
        accounts = pack_config.get("smtp_accounts", None)
        if not accounts:
            raise ValueError(
                f"'smtp_account' config value is required to send email, config={pack_config}"
            )
        try:
            key_value = {a["name"]: a for a in accounts}
            account_data = key_value[smtp_account]
        except KeyError as exc:
            raise KeyError(
                f"The account {smtp_account} does not appear in the configuration"
            ) from exc

        return account_data

    def attach_files(self, msg: MIMEMultipart, files):
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

    # pylint:disable=too-many-arguments
    def send_email(
        self,
        pack_config: Dict,
        subject: str,
        email_to: List[str],
        email_from: str,
        email_cc: str,
        header: str,
        footer: str,
        body: str,
        attachment_filepaths: List[str],
        smtp_account: Dict[str],
        send_as_html: bool,
    ):
        """
        Send an email
        :param: pack_config (Dict): Pack config (containing smtp_account)
        :param: subject: (String): Subject of the email
        :param: email_to (List[String]): Email addresses to send the email to
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: header (String): filepath to header file,
        :param: footer (String): filepath to footer file,
        :param: body (String): body of email,
        :param: attachment_filepaths (List): list of attachment filepaths,
        :param: smtp_account (String): email config to use,
        :param: send_as_html (Bool): If true will send in HTML format
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """

        account_data = self.load_smtp_account(pack_config, smtp_account)

        msg = MIMEMultipart()
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = email_from
        msg["To"] = ", ".join(email_to)

        msg["Date"] = formatdate(localtime=True)

        header = self.load_template(header)
        footer = self.load_template(footer)

        if send_as_html:
            msg.attach(
                MIMEText(
                    f"""\
            <html>
                <head>
                <style>
                    table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
                    th, td {{ padding: 8px; }}
                </style>
                </head>
                <body>
                    {header}
                    {body}
                    {footer}
                </body>
            </html>
            """,
                    "html",
                )
            )
        else:
            msg.attach(MIMEText(f"{header}\n{body}\n{footer}", "plain", "utf-8"))

        if email_cc:
            msg["Cc"] = ", ".join(email_cc)

        if len(attachment_filepaths) > 0:
            self.attach_files(msg, attachment_filepaths)

        smtp = SMTP_SSL(account_data["server"], str(account_data["port"]), timeout=60)
        smtp.ehlo()

        if account_data.get("secure", True):
            smtp.starttls()
        if account_data.get("smtp_auth", True):
            smtp.login(account_data["username"], account_data["password"])

        email_to = (email_to + email_cc) if email_cc else email_to

        smtp.sendmail(email_from, email_to, msg.as_string())
        smtp.quit()
        return (True, "Email sent")

    # pylint:disable=too-many-arguments
    def send_emails(
        self,
        pack_config: Dict,
        emails: Dict[str, str],
        subject: str,
        email_from: str,
        email_cc: List[str],
        header: str,
        footer: str,
        attachment_filepaths: List[str],
        smtp_account: Dict[str],
        test_override: bool,
        test_override_email: List[str],
        send_as_html: bool,
    ):
        """
        Sends multiple emails
        :param: pack_config (Dict): Pack config (containing smtp_account)
        :emails (Dict): Keys are email addresses, values are messages to send to those emails
        :param: subject: (String): Subject of the email
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: header (String): filepath to header file,
        :param: footer (String): filepath to footer file,
        :param: attachment (List): list of attachment filepaths,
        :param: smtp_account (String): email config to use,
        :param: test_override (Boolean): send all emails to test emails
        :param: test_override_email (List[String]): send to this email if test_override enabled
        :param: send_as_html (Bool): If true will send in HTML format
        :return: Status (Bool): tuple of action status (succeeded(T)/failed(F)) and the output
        """
        if test_override:
            # Send a maximum of 10 emails
            emails = dict(random.sample(emails.items(), min(len(emails), 10)))

            return all(
                [
                    self.send_email(
                        pack_config,
                        subject=subject,
                        email_to=test_override_email,
                        email_from=email_from,
                        email_cc=email_cc,
                        header=header,
                        footer=footer,
                        body=value,
                        attachment_filepaths=attachment_filepaths,
                        smtp_account=smtp_account,
                        send_as_html=send_as_html,
                    )[0]
                ]
                for key, value in emails.items()
            )

        return all(
            [
                self.send_email(
                    pack_config,
                    subject=subject,
                    email_to=[key],
                    email_from=email_from,
                    email_cc=email_cc,
                    header=header,
                    footer=footer,
                    body=value,
                    attachment_filepaths=attachment_filepaths,
                    smtp_account=smtp_account,
                    send_as_html=send_as_html,
                )[0]
            ]
            for key, value in emails.items()
        )
