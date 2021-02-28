# -*- coding: utf-8 -*-
"""
    Module containing various miscellaneous utility functions and classes.
"""

##### IMPORTS #####
# Standard imports
import logging
from logging import handlers


##### CONSTANTS #####
LOG = logging.getLogger(__name__)


##### CLASSES #####
class Logger:
    """Context manager class for initialising and managing the logger."""

    LOG_NAME = "banalysis.log"

    def __init__(self):
        self.path = self.LOG_NAME
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        fh = handlers.RotatingFileHandler(self.path, maxBytes=1e6, backupCount=1)
        fh.setLevel(logging.DEBUG)
        f_fmt = logging.Formatter(
            "{asctime} [{threadName:10.10}] [{name:20.20}] "
            "[{levelname:7.7}] {message}",
            style="{",
        )
        fh.setFormatter(f_fmt)
        self.logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setLevel(logging.WARN)
        s_fmt = logging.Formatter("[{levelname}] {message}", style="{")
        sh.setFormatter(s_fmt)
        self.logger.addHandler(sh)

        self.logger.debug("Initialised logger")

    def __enter__(self):
        return self

    def __exit__(self, excepType, excepVal, traceback):
        """Writes error traceback and closes log file."""
        if isinstance(excepVal, SystemExit) and excepVal.args[0] == 0:
            LOG.info("Program exited sucessfully")
        elif excepType is not None or excepVal is not None or traceback is not None:
            LOG.critical("A critical error occurred", exc_info=True)
        else:
            LOG.info("Program completed without any critical errors")
        logging.shutdown()
