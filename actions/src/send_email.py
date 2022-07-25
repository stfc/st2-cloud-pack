import os
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from st2common.runners.base_action import Action


class SendEmail(Action):
    def run(self, **kwargs):
        """
        function that is run by stackstorm when an action is invoked
        :param kwargs: arguments for openstack actions
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """
        if "body" in kwargs and kwargs["body"]:
            return self.send_email(**kwargs)
        return None

    # pylint: disable=too-many-locals,too-many-branches
    def send_email(self, **kwargs):
        """
        Send email
        :param kwargs: email_to (String): Recipient Email,
        email_from (String): Sender Email, subject (String): Email Subject,
        header (String): filepath to header file,
        footer (String): filepath to footer file,
        body (String): body of email,
        attachment (List): list of attachment filepaths,
        smtp_account (String): email config to use,
        admin_override (Boolean): send all emails to admin email - testing purposes,
        admin_override_email (String): send to this email if admin_override enabled
        :return:
        """

        accounts = self.config.get("smtp_accounts", None)
        if not accounts:
            raise ValueError(
                f"'smtp_account' config value is required to send email, config={self.config}"
            )
        try:
            key_value = {a["name"]: a for a in accounts}
            account_data = key_value[kwargs["smtp_account"]]
        except KeyError as exc:
            raise KeyError(
                f"The account {kwargs['smtp_account']} does not appear in the configuration"
            ) from exc

        msg = MIMEMultipart()
        msg["Subject"] = Header(kwargs["subject"], "utf-8")
        msg["From"] = kwargs["email_from"]
        msg["To"] = ", ".join(kwargs["email_to"])

        if kwargs["admin_override"]:
            msg["To"] = ", ".join(kwargs["admin_override_email"])

        msg["Date"] = formatdate(localtime=True)

        if "header" in kwargs and os.path.exists(kwargs["header"]):
            with open(kwargs["header"], "r", encoding="utf-8") as header_file:
                header = header_file.read()
        if "footer" in kwargs and os.path.exists(kwargs["footer"]):
            with open(kwargs["footer"], "r", encoding="utf-8") as footer_file:
                footer = footer_file.read()

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
        attachments = kwargs["attachment_filepaths"] or tuple()
        for filepath in attachments:
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as file:
                part = MIMEApplication(file.read(), Name=filename)
            part["Content-Disposition"] = f"attachment; filename={filename}"
            msg.attach(part)

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
