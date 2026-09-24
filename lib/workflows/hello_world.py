import logging

logger = logging.getLogger(__name__)


def salute():
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent
    conf_path = BASE_DIR / "etc/config"
    print(conf_path)
    #conf = open("etc/config")
    conf = open(conf_path)
    logger.info("Hello!!")
    logger.info(conf.readlines())
