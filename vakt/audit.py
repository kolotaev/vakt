"""
Audit logging for Vakt decisions.
"""

import logging


LOG_NAME = 'VaktAuditLog'


class AuditLogger(logging.getLoggerClass()):
    def __init__(self, enabled=True):
        self._enabled = enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False


def get_logger():
    """Get logger for audit"""
    log = logging.getLogger(LOG_NAME)
    log.addFilter(LogFilter())
    log.setLevel(logging.INFO)
    return log


def enable():
    """Enables audit logging"""
    LogFilter._do_log = True


def disable():
    """Disables audit logging"""
    LogFilter._do_log = False


class LogFilter(logging.Filter):
    """
    Filter that is attached to audit-log logger.
    Allows logging to 'VaktAuditLog' if audit-log is enabled.
    Disabled by default.
    """
    _do_log = False

    def filter(self, record):
        return self._do_log
