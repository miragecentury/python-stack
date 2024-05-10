"""Provide Logging Filters"""

import logging
from logging import LogRecord


class StdoutFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """Filter to accept only level lower than Error"""

    def filter(self, record: LogRecord) -> bool:
        """filter by log Level"""
        return logging.ERROR > record.levelno


class StderrFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """Filter to accept only level upper or egal than Error"""

    def filter(self, record: LogRecord) -> bool:
        """filter by log Level"""
        return logging.ERROR <= record.levelno
