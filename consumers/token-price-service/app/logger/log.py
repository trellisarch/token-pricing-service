import logging.config
import json
import os
from logging import Logger

from app.config.config import Config


def get_logger() -> Logger:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_config_path = os.path.join(current_dir, Config.LOG_CONFIG_PATH)

    with open(log_config_path, "r") as f:
        log_config = json.load(f)

        logger = logging.getLogger("pricing_service")
        if not logger.hasHandlers():
            logger.setLevel(logging.DEBUG)
            logging.config.dictConfig(log_config)
            return logger
        else:
            return logger
