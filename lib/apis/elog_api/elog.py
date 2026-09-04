import logging
from apis.elog_api.structs.elog_account import ElogAccount

logger = logging.getLogger(__name__)


def add_record_to_elog(elog_account: ElogAccount, subject: str, body: str) -> None:
    """
    adds a new record to the ELOG server

    :param subject: the title of the new record
    :type subject: str
    :param body: the text that goes in the record
    :type body: str
    """
    logger.info("Adding a new record to ELOG")
    logger.info("subject = %s", subject)
    logger.info("body = %s", body)
    entry_data = {
        "cmd": "Submit",
        "Category": "Routine",
        "Subject": subject,
        "Author": elog_account.username,
        "Encoding": "plain",
        "Text": body,
    }
    session = elog_account.authenticate()
    submit_response = session.post(
        elog_account.elog_endpoint,
        files={k: (None, v) for k, v in entry_data.items()},
    )
    submit_response.raise_for_status()
    logger.debug("HTTP Status: %s", submit_response.status_code)
    logger.debug(submit_response.text)
    logger.info("New record added successfully to ELOG")
