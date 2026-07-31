from __future__ import annotations

import logging
import sys

GATEWAY_LOGGER_NAME = "agentforge.gateway"

SUPPORTED_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


def get_logger() -> logging.Logger:
    return logging.getLogger(GATEWAY_LOGGER_NAME)


def configure_logging(level: str = "INFO") -> None:
    logger = get_logger()
    logger.setLevel(level.upper())
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    logger.propagate = False
