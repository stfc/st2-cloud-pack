import logging

logger = logging.getLogger(__name__)


def salute():
    conf = open("etc/config")
    logger.info("Hello!!")
    logger.info(conf.readlines())
