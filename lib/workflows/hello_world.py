import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def salute():
    BASE_DIR = Path(__file__).resolve().parent
    logger.info(BASE_DIR)
    conf_path = BASE_DIR / "etc/config"
    conf = open(conf_path)
    logger.info("Hello!!")
    logger.info(conf.readlines())
