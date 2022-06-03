import logging
from logging import Logger


def get_logger(name: str) -> Logger:
    _logger: Logger = logging.getLogger(name)
    _logger.setLevel(logging.INFO)
    _logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    _logger.addHandler(handler)
    return _logger
