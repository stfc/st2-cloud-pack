import os
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Dict


class EmailApi:
    def load_template(self, prop, **kwargs):
        """
        Loads and returns a html template from its path
        :param prop: Name of the property in kwargs containing the path
                     to the template
        :param kwargs: Arguments for the action
        :return: (String) The contents of the file in utf-8 format
        """
        if prop in kwargs:
            path = kwargs[prop]
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as header_file:
                    return header_file.read()
            else:
                raise FileNotFoundError(f"Template file located {path} not found")
        else:
            raise KeyError(f"The property {prop} does not appear in the configuration")

    def load_smtp_account(self, pack_config: Dict, **kwargs):
        """
        Loads and returns the smtp account data from the pack config
        :param pack_config: The config for the pack
        :param kwargs: Arguments for the action
        :return: (Dictionary) SMTP account properties
        """
        accounts = pack_config.get("smtp_accounts", None)
        if not accounts:
            raise ValueError(
                f"'smtp_account' config value is required to send email, config={pack_config}"
            )
        try:
            key_value = {a["name"]: a for a in accounts}
            account_data = key_value[kwargs["smtp_account"]]
        except KeyError as exc:
            raise KeyError(
                f"The account {kwargs['smtp_account']} does not appear in the configuration"
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

    def send_email(self, pack_config: Dict, **kwargs):
        """
        Send email
        :pack_config (Dict): Pack config (containing smtp_account)
        :param kwargs: email_to (String): Recipient Email,
        email_from (String): Sender Email, subject (String): Email Subject,
        header (String): filepath to header file,
        footer (String): filepath to footer file,
        body (String): body of email,
        attachment (List): list of attachment filepaths,
        smtp_account (String): email config to use,
        admin_override (Boolean): send all emails to admin email - testing purposes,
        admin_override_email (String): send to this email if admin_override enabled
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """

        account_data = self.load_smtp_account(pack_config, **kwargs)

        msg = MIMEMultipart()
        msg["Subject"] = Header(kwargs["subject"], "utf-8")
        msg["From"] = kwargs["email_from"]
        msg["To"] = ", ".join(kwargs["email_to"])

        if kwargs["admin_override"]:
            msg["To"] = ", ".join(kwargs["admin_override_email"])

        msg["Date"] = formatdate(localtime=True)

        header = self.load_template("header", **kwargs)
        footer = self.load_template("footer", **kwargs)

        if kwargs["send_as_html"]:
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
                    {kwargs["body"]}
                    {footer}
                </body>
            </html>
            """,
                    "html",
                )
            )
        else:
            msg.attach(
                MIMEText(f"{header}\n{kwargs['body']}\n{footer}", "plain", "utf-8")
            )

        if kwargs["email_cc"]:
            msg["Cc"] = ", ".join(kwargs["email_cc"])
        self.attach_files(msg, kwargs["attachment_filepaths"] or tuple())

        smtp = SMTP_SSL(account_data["server"], str(account_data["port"]), timeout=60)
        smtp.ehlo()

        if account_data.get("secure", True):
            smtp.starttls()
        if account_data.get("smtp_auth", True):
            smtp.login(account_data["username"], account_data["password"])

        if kwargs["admin_override"]:
            email_to = kwargs["admin_override_email"]
        else:
            email_to = (
                (kwargs["email_to"] + kwargs["email_cc"])
                if kwargs["email_cc"]
                else kwargs["email_to"]
            )

        smtp.sendmail(kwargs["email_from"], email_to, msg.as_string())
        smtp.quit()
        return (True, "Email sent")
