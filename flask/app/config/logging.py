import os
import logging

# from logging.handlers import RotatingFileHandler
from logging import StreamHandler
import sys


def config_logging(app):
    stdout_handler = StreamHandler(sys.stdout)

    stdout_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    )
    stdout_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(stdout_handler)

    # if not app.debug:
    #     # if not os.path.exists("logs"):
    #     #     os.mkdir("logs")

    #     # file_handler = RotatingFileHandler(
    #     #     "logs/api.log", maxBytes=10240, backupCount=10
    #     # )

    #     # file_handler.setFormatter(
    #     #     logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    #     # )
    #     # file_handler.setLevel(logging.DEBUG)
    #     # app.logger.addHandler(file_handler)
