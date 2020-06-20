"""
Audit logging for Vakt decisions.
"""

import logging


LOGGER_NAME = 'VaktAuditLog'


def get_logger(record_class):
    """
    Get logger for audit
    """

    def record_factory(*args, **kwargs):
        return record_class(*args, **kwargs)

    log = logging.getLogger(LOGGER_NAME)
    log.setLogRecordFactory(record_factory)
    # log.addFilter(LogFilter())
    # log.setLevel(logging.INFO)
    return log


class NopLogRecord(logging.LogRecord):
    def getMessage(self):
        return None


class InquiryLogRecord(logging.LogRecord):
    def getMessage(self):
        return '%s inquiry %s' % (self.msg, self.args['inquiry'])


class DecidersLogRecord(logging.LogRecord):
    def getMessage(self):
        deciders = list(map(lambda x: x.uid, self.args['deciders']))
        return '%s inquiry %s by deciding policies %s' % (self.msg, self.args['inquiry'], deciders)


class FullLogRecord(logging.LogRecord):
    def getMessage(self):
        policies = list(map(lambda x: x.uid, self.args['policies']))
        deciders = list(map(lambda x: x.uid, self.args['deciders']))
        return '%s inquiry %s by deciding policies %s using all filtered policies %s' % \
               (self.msg, self.args['inquiry'], deciders, policies)


# class LogFilter(logging.Filter):
#     """
#     Filter that is attached to audit-log logger.
#     Allows logging to 'VaktAuditLog' if audit-log is enabled.
#     Disabled by default.
#     """
#     _do_log = False
#
#     def filter(self, record):
#         return self._do_log

#
# class AuditLogger(logging.getLoggerClass()):
#     def __init__(self, enabled=True):
#         self._enabled = enabled
#         self.addFilter(LogFilter())
#         self.setLevel(logging.INFO)
#
#     def enable(self):
#         self._enabled = True
#
#     def disable(self):
#         self._enabled = False

#
#
# def enable():
#     """Enables audit logging"""
#     LogFilter._do_log = True
#
#
# def disable():
#     """Disables audit logging"""
#     LogFilter._do_log = False
#
