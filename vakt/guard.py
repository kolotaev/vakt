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
        return cls(props.get('resource'),
                   props.get('action'),
                   props.get('subject'),
                   props.get('context'))


# todo - add info-level logging
class Guard:
    """Executor of policy checks.
       Given a storage and a matcher it can decide via `is_allowed` method if a given inquiry allowed or not."""

    def __init__(self, storage, matcher):
        self.storage = storage
        self.matcher = matcher

    def is_allowed(self, inquiry):
        """Is given inquiry intent allowed or not?"""
        try:
            policies = self.storage.find_by_inquiry(inquiry)
            if not policies:
                return False
            else:
                # Storage is not obliged to do the exact policies match. It's up to the storage
                # to decide what policies to return. So we need a more correct programmatically done check.
                return self.check_policies_allow(inquiry, policies)
        except Exception:
            log.exception('Unexpected exception occurred while checking Inquiry %s', inquiry)
            return False

    def check_policies_allow(self, inquiry, policies):
        """Check if any of a given policy allows a specified inquiry"""
        allow = False
        for p in policies:
            # First we check if action is OK. Since usually action is the most used check.
            if not self.matcher.matches(p, 'actions', inquiry.action):
                continue
            # Subject is a more quick check then resources, so we try it second.
            if not self.matcher.matches(p, 'subjects', inquiry.subject):
                continue
            # Check for resources access
            if not self.matcher.matches(p, 'resources', inquiry.resource):
                continue
            # Lastly check if the given inquiry's context satisfies rules of a policy
            if not self.are_rules_satisfied(p, inquiry):
                continue
            # If policy passed all matches - it's the right policy and all we need is to check its allow-effect.
            # If we have 2 or more matched policies and one of them has deny access - it's deny for all of them.
            if not p.allow_access():
                return False
            allow = True
        return allow

    @staticmethod
    def are_rules_satisfied(policy, inquiry):
        """Check if rules in the policy are satisfied for a given inquiry's context"""
        for key, rule in policy.rules.items():
            try:
                ctx_rule = inquiry.context[key]
            except KeyError:
                # todo - do we need it?
                return False
            if not rule.satisfied(ctx_rule, inquiry):
                return False
        return True
