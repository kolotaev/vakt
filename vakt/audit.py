"""
Audit logging for Vakt decisions.
"""

import logging
from operator import attrgetter


from .effects import ALLOW_ACCESS


LOGGER_NAME = 'VaktAuditLog'


def get_logger():
    """
    Get logger for audit
    """

    # def record_factory(*args, **kwargs):
    #     return record_class(*args, **kwargs)

    log = logging.getLogger(LOGGER_NAME)
    # log.setLogRecordFactory(record_factory)
    # log.addFilter(LogFilter())
    # log.setLevel(logging.INFO)
    return log


def set_message_class(cl):
    global _MESSAGE_CLASS
    _MESSAGE_CLASS = cl


def message():
    return _MESSAGE_CLASS


class NopMsg:
    def __str__(self):
        return ''


class EffectMsg:
    def __init__(self, effect, inquiry, policies, deciders):
        self.effect = effect
        self.inquiry = inquiry
        self.policies = policies
        self.deciders = deciders

    def __str__(self):
        if self.effect == ALLOW_ACCESS:
            return 'Allowed'
        return 'Denied'

    __repr__ = __str__


class InquiryMsg(EffectMsg):
    def __str__(self):
        return '%s inquiry %s' % (self, self.inquiry)


class DecidersMsg(InquiryMsg):
    def __str__(self):
        return '%s by deciding policies %s' % (self, list(map(attrgetter('uid'), self.deciders)))


class FullMsg(DecidersMsg):
    def __str__(self):
        return '%s using all candidate policies %s' % (self, list(map(attrgetter('uid'), self.policies)))


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

_MESSAGE_CLASS = DecidersMsg
