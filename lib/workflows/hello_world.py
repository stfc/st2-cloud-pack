import logging

logger = logging.getLogger(__name__)


def salute():
    conf = file("etc/config")
    logger.info("Hello!!")
    logger.info(conf.readlines())
