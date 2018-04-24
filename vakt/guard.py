""""
Main module that serves as an entry point for Vakt decisions.
Also contains Inquiry class.
"""

import logging

from .util import JsonDumper, PrettyPrint


log = logging.getLogger(__name__)


class Inquiry(JsonDumper, PrettyPrint):
    """Holds all the information about the inquired intent.
    Is responsible to decisions is the inquired intent allowed or not."""

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


class Guard:
    """Executor of policy checks.
       Given a storage and a checker it can decide via `is_allowed` method if a given inquiry allowed or not."""

    def __init__(self, storage, checker):
        self.storage = storage
        self.checker = checker

    def is_allowed(self, inquiry):
        """Is given inquiry intent allowed or not?"""
        try:
            policies = self.storage.find_for_inquiry(inquiry)
            # Storage is not obliged to do the exact policies match. It's up to the storage
            # to decide what policies to return. So we need a more correct programmatically done check.
            answer = self.check_policies_allow(inquiry, policies)
        except Exception:
            log.exception('Unexpected exception occurred while checking Inquiry %s', inquiry)
            answer = False

        if answer:
            log.info('Incoming Inquiry allowed. Data: %s', inquiry)
        else:
            log.info('Incoming Inquiry rejected. Data: %s', inquiry)

        return answer

    def check_policies_allow(self, inquiry, policies):
        """Check if any of a given policy allows a specified inquiry"""
        # If no policies found or None is given -> deny access!
        if not policies:
            return False

        # Filter policies that fit Inquiry by its attributes.
        filtered = [p for p in policies if
                    self.checker.fits(p, 'actions', inquiry.action) and
                    self.checker.fits(p, 'subjects', inquiry.subject) and
                    self.checker.fits(p, 'resources', inquiry.resource) and
                    self.are_rules_satisfied(p, inquiry)]

        # no policies -> deny access!
        # if we have 2 or more similar policies - all of them should have allow effect, otherwise -> deny access!
        return len(filtered) > 0 and all(p.allow_access() for p in filtered)

    @staticmethod
    def are_rules_satisfied(policy, inquiry):
        """Check if rules in the policy are satisfied for a given inquiry's context"""
        for key, rule in policy.rules.items():
            try:
                ctx_rule = inquiry.context[key]
            except KeyError:
                return False
            if not rule.satisfied(ctx_rule, inquiry):
                return False
        return True
