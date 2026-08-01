import logging
from logging import Logger

logging.basicConfig(
level=logging.INFO,
format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def get_logger(name: str = __name__) -> logging.Logger:
    return logging.getLogger(name)
