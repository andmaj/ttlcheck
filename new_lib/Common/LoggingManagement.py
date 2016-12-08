import logging
import sys

ch = logging.StreamHandler(sys.stdout)


def get_logger(name):
    logger = logging.getLogger(name)

    ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

    return logger
