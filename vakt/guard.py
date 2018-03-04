import logging

from .util import JsonDumper, PrettyPrint


log = logging.getLogger(__name__)


class Request(JsonDumper, PrettyPrint):
    """Request object that holds all the information about the requested resource intent.
    Is responsible to decisions is the requested intent allowed or not."""

    def __init__(self, resource=None, action=None, subject=None, context=None):
        # explicitly assign empty strings instead of occasional None, (), etc.
        self.resource = resource or ''
        self.action = action or ''
        self.subject = subject or ''
        self.context = context or {}

    @classmethod
    def from_json(cls, data):
        props = cls._parse(data)
        return cls(props.get('resource', ''),
                   props.get('action', ''),
                   props.get('subject', ''),
                   props.get('context'))


# todo - add info-level logging
class Guard:
    """Executor of policy checks.
       Given a manager and a matcher it can decide via `is_allowed` method if a given request allowed or not."""

    def __init__(self, manager, matcher):
        self.manager = manager
        self.matcher = matcher

    def is_allowed(self, request):
        """Is given request intent allowed or not?"""
        try:
            policies = self.manager.find_by_request(request)
            if not policies:
                return False
            else:
                # Manager is not obliged to do the exact policies match. It's up to the manager
                # to decide what policies to return. So we need a more correct programmatically done check.
                return self.check_policies_allow(request, policies)
        except Exception:
            log.exception('Unexpected exception occurred while checking Request %s', request)
            return False

    def check_policies_allow(self, request, policies):
        """Check if any of a given policy allows a specified request"""
        allow = False
        for p in policies:
            # First we check if action is OK. Since usually action is the most used check.
            if not self.matcher.matches(p, 'actions', request.action):
                continue
            # Subject is a more quick check then resources, so we try it second.
            if not self.matcher.matches(p, 'subjects', request.subject):
                continue
            # Check for resources access
            if not self.matcher.matches(p, 'resources', request.resource):
                continue
            # Lastly check if the given request's context satisfies conditions of a policy
            if not self.are_conditions_satisfied(p, request):
                continue
            # If policy passed all matches - it's the right policy and all we need is to check its allow-effect.
            # If we have 2 or more matched policies and one of them has deny access - it's deny for all of them.
            if not p.allow_access():
                return False
            allow = True
        return allow

    @staticmethod
    def are_conditions_satisfied(policy, request):
        """Check if conditions in the policy are satisfied for a given request's context"""
        for key, condition in policy.conditions.items():
            try:
                ctx_condition = request.context[key]
            except KeyError:
                # todo - do we need it?
                return False
            if not condition.satisfied(ctx_condition, request):
                return False
        return True
