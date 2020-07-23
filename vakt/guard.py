""""
Main module that serves as an entry point for Vakt decisions.
Also contains Inquiry class.
"""

import logging

from .util import JsonSerializer, PrettyPrint
from .audit import PoliciesUidMsg, __name__ as audit_module_name
from .effects import ALLOW_ACCESS, DENY_ACCESS

log = logging.getLogger(__name__)
audit_log = logging.getLogger(audit_module_name)


class Inquiry(JsonSerializer, PrettyPrint):
    """Holds all the information about the inquired intent.
    Is responsible to decisions if the inquired intent allowed or not."""

    def __init__(self, resource=None, action=None, subject=None, context=None):
        # explicitly assign empty strings instead of occasional None, (), etc.
        self.resource = resource or ''
        self.action = action or ''
        self.subject = subject or ''
        self.context = context or {}

    @classmethod
    def from_json(cls, data):
        props = cls._parse(data)
        return cls(**props)

    def to_json_sorted(self):
        """
        Get JSON representation with all keys sorted.
        """
        return super().to_json(sort=True)

    def __eq__(self, other):
        """
        If inquiries have the same contents - they are equal
        """
        return self.to_json_sorted() == other.to_json_sorted()

    def __hash__(self):
        """
        We do not use to_json as contents representation, because strings are not guaranteed
        to be hashed consistently across different python processes.
        """
        return hash(tuple((ord(c) for c in self.to_json_sorted())))


class Guard:
    """
    Executor of policy checks.
    Given a storage and a checker it can decide via `is_allowed` method if a given inquiry allowed or not.

    storage - what storage to use
    checker - what checker to use
    audit_policies_cls - what message class to use for logging Policies in audit
    """

    def __init__(self, storage, checker, audit_policies_cls=None):
        self.storage = storage
        self.checker = checker
        self.apm = audit_policies_cls
        if self.apm is None:
            self.apm = PoliciesUidMsg

    def is_allowed(self, inquiry):
        """
        Is given inquiry intent allowed or not?
        Same as `is_allowed_check`, but also logs policy enforcement decisions to log for every incoming inquiry.
        Is meant to be used by an end-user.
        """
        answer = self.is_allowed_check(inquiry)
        if answer:
            log.info('Incoming Inquiry was allowed. Inquiry: %s', inquiry)
        else:
            log.info('Incoming Inquiry was rejected. Inquiry: %s', inquiry)
        return answer

    def is_allowed_check(self, inquiry):
        """
        Is given inquiry intent allowed or not?
        Does not log answers to 'vakt.guard' log-stream.
        Is not meant to be called by an end-user. Use it only if you want the core functionality of allowance check.
        """
        try:
            policies = self.storage.find_for_inquiry(inquiry, self.checker)
            # A safe guard against custom Storages that may return None instead of an empty list
            if policies is None:
                log.error('Storage returned None, but is supposed to return at least an empty list')
                return False
            # Storage is not obliged to do the exact policies match. It's up to the storage
            # to decide what policies to return. So we need a more correct programmatically done check.
            answer = self.check_policies_allow(inquiry, policies)
        except Exception:
            log.exception('Unexpected exception occurred while checking Inquiry %s', inquiry)
            answer = False
        return answer

    def check_policies_allow(self, inquiry, policies):
        """
        Check if any of a given policy allows a specified inquiry
        """
        # Filter policies that fit Inquiry by its attributes.
        filtered = [p for p in policies if
                    self.checker.fits(p, 'actions', inquiry.action, inquiry) and
                    self.checker.fits(p, 'subjects', inquiry.subject, inquiry) and
                    self.checker.fits(p, 'resources', inquiry.resource, inquiry) and
                    self.check_context_restriction(p, inquiry)]

        # no policies -> deny access!
        if len(filtered) == 0:
            audit_log.info('No potential policies were found', extra={
                'effect': DENY_ACCESS, 'inquiry': inquiry,
                'candidates': self.apm(filtered), 'deciders': self.apm([]),
            })
            return False

        # if we have 2 or more similar policies - all of them should have allow effect, otherwise -> deny access!
        for p in filtered:
            if not p.allow_access():
                audit_log.info('One of matching policies has deny effect', extra={
                    'effect': DENY_ACCESS, 'inquiry': inquiry,
                    'candidates': self.apm(filtered), 'deciders': self.apm([p]),
                })
                return False

        audit_log.info('All matching policies have allow effect', extra={
            'effect': ALLOW_ACCESS, 'inquiry': inquiry,
            'candidates': self.apm(filtered), 'deciders': self.apm(filtered),
        })
        return True

    @staticmethod
    def check_context_restriction(policy, inquiry):
        """
        Check if context restriction in the policy is satisfied for a given inquiry's context.
        If at least one rule is not present in Inquiry's context -> deny access.
        If at least one rule provided in Inquiry's context is not satisfied -> deny access.
        """
        for key, rule in policy.context.items():
            try:
                ctx_value = inquiry.context[key]
            except KeyError:
                log.debug("No key '%s' found in Inquiry context", key)
                return False
            if not rule.satisfied(ctx_value, inquiry):
                return False
        return True
