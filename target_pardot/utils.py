import logging, sys


LOGGER = None


def get_logger(name="handoff", level=logging.INFO):
    global LOGGER

    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "warn": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    if type(level) == str:
        level = levels[level.lower()]

    if not LOGGER:
        logging.basicConfig(
            stream=sys.stdout,
            format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
            level=level)
        LOGGER = logging.getLogger(name)

    return LOGGER
