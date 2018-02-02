import json

from .util import JsonDumper


class Request(JsonDumper):
    """Request object that holds all the information about the requested resource intent.
    Is responsible to decisions is the requested intent allowed or not."""

    def __init__(self, resource, action, subject, context=None):
        self.resource = resource
        self.action = action
        self.subject = subject
        self.context = context

    @classmethod
    def from_json(cls, data):
        try:
            props = json.loads(data)
        except json.JSONDecodeError as e:
            # todo - logging
            # print("Error creating policy from json.", e)
            raise e

        return cls(props.get('resource', ''),
                   props.get('action', ''),
                   props.get('subject', ''),
                   props.get('context'))


class Guard:
    """Executor of policy checks.
       Given a manager and a matcher it can decide via `is_allowed` method if a given request allowed or not."""

    def __init__(self, manager, matcher):
        self.manager = manager
        self.matcher = matcher

    def is_allowed(self, request):
        """Is given request intent allowed or not?"""
        policies = self.manager.find_by_request(request)
        if policies is None or len(policies) == 0:
            return False
        else:
            return self._check_policies_allow(request, policies)

    def _check_policies_allow(self, request, policies):
        """Check if any of a given policy allows a specified request"""
        allow = False
        for p in policies:
            # First we check if action is OK. Since usually action is the most used check.
            if not self.matcher.matches(p, 'actions', request.action):
                continue
            # Subject is a more quick check then resources, so we try it second.
            if not self.matcher.matches(p, 'subjects', request.subject):
                continue
            if not self.matcher.matches(p, 'resources', request.resource):
                continue
            if not self._conditions_satisfied(p, request):
                continue
            if not p.allow_access:
                return False
            allow = True
        return allow

    @staticmethod
    def _conditions_satisfied(policy, request):
        """Check if conditions in the policy are satisfied for a given request"""
        for key, condition in enumerate(policy.conditions):
            try:
                ctx_condition = request.context[key]
            except KeyError:
                return False
            if not condition.satisfied(ctx_condition, request):
                return False
        return True
