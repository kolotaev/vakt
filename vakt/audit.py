"""
Audit logging for Vakt decisions.
"""

import logging
from operator import attrgetter

# LOGGER_NAME = 'VaktAuditLog'

log = logging.getLogger(__name__)

POLICIES_MSG_CLASS = None


def policies_message_class():
    """
    Get class responsible for printing policies collection.
    """
    if POLICIES_MSG_CLASS is None:
        return PoliciesUidMsg
    return POLICIES_MSG_CLASS


class PoliciesNopMsg:
    def __init__(self, policies=()):
        pass

    def __str__(self):
        return ''


class PoliciesUidMsg:
    def __init__(self, policies=()):
        self.policies = policies

    def __str__(self):
        uids = list(map(attrgetter('uid'), self.policies))
        return '[%s]' % ','.join(map(str, uids))


class PoliciesDescriptionMsg(PoliciesUidMsg):
    def __str__(self):
        descriptions = list(map(attrgetter('description'), self.policies))
        return '[%s]' % ','.join(map(lambda x: "'%s'" % x, descriptions))


class PoliciesCountMsg(PoliciesUidMsg):
    def __str__(self):
        return 'count = %d' % len(self.policies)


# class AuditContextFilter(logging.Filter):
#     """
#     This is a filter which injects audit contextual information into the log.
#     """
#     def filter(self, record):
#         # record.effect = 'Unknown'
#         # record.inquiry = 'None'
#         # record.policies = '[]'
#         # record.deciders = '[]'
#         # return True
#         return super().filter(record)


# log.addFilter(AuditContextFilter())


# def log(*args, **kwargs):
#     get_logger.info(args, kwargs)
#
#
# def get_logger():
#     global _logger
#     if _logger is None:
#         _logger = logging.getLogger(LOGGER_NAME)
#         # log.setLogRecordFactory(record_factory)
#         _logger.addFilter(AuditContextFilter)
#         # log.setLevel(logging.INFO)
#     return _logger


# def _get_logger():
#     """
#     Get logger for audit
#     """
#     # old_factory = logging.getLogRecordFactory()
#     #
#     # def record_factory(*args, **kwargs):
#     #     record = old_factory(*args, **kwargs)
#     #     record.custom_attribute = 0xdecafbad
#     #     return record
#
#     log = logging.getLogger(LOGGER_NAME)
#     # log.setLogRecordFactory(record_factory)
#     log.addFilter(AuditContextFilter)
#     # log.setLevel(logging.INFO)
#     return log

#
#
# def set_message_class(cl):
#     global _MESSAGE_CLASS
#     _MESSAGE_CLASS = cl
#
#
# def message():
#     return _MESSAGE_CLASS
#
#
# class NopMsg:
#     def __str__(self):
#         return ''
#
#
# class EffectMsg:
#     def __init__(self, effect, inquiry, policies, deciders):
#         self.effect = effect
#         self.inquiry = inquiry
#         self.policies = policies
#         self.deciders = deciders
#
#     def __str__(self):
#         if self.effect == ALLOW_ACCESS:
#             return 'Allowed'
#         return 'Denied'
#
#     __repr__ = __str__
#
#
# class InquiryMsg(EffectMsg):
#     def __str__(self):
#         return '%s inquiry %s' % (self, self.inquiry)
#
#
# class DecidersMsg(InquiryMsg):
#     def __str__(self):
#         return '%s by deciding policies %s' % (self, list(map(attrgetter('uid'), self.deciders)))
#
#
# class FullMsg(DecidersMsg):
#     def __str__(self):
#         return '%s using all candidate policies %s' % (self, list(map(attrgetter('uid'), self.policies)))
#
#
# _MESSAGE_CLASS = DecidersMsg
#
#
#


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
