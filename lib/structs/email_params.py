from dataclasses import dataclass
from typing import List


@dataclass
class EmailParams:
    """
    Email parameters that are shared between the send_email and send_emails functions in EmailApi
    :param: subject: (String): Subject of the email
    :param: email_from (String): Sender Email, subject (String): Email Subject,
    :param: email_cc (List[String]): Email addresses to Cc
    :param: header (String): filepath to header file,
    :param: footer (String): filepath to footer file,
    :param: attachment_filepaths (List): list of attachment filepaths,
    :param: send_as_html (Bool): If true will send in HTML format
    :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
    """

    subject: str
    email_from: str
    email_cc: List[str]
    header: str
    footer: str
    attachment_filepaths: List[str]
    test_override: bool
    test_override_email: List[str]
    send_as_html: bool
