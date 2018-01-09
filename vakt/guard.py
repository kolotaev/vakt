from vakt.util import JsonDumper


class Request(JsonDumper):
    """Request object that holds all the information about the requested resource intent.
    Is responsible to decisions is the requested intent allowed or not."""

    def __init__(self, resource, action, subject, context=None):
        self.resource = resource
        self.action = action
        self.subject = subject
        self.context = context


class Guard:
    """Executor of policy checks.
       Given a manager and a matcher it can decide via `is_allowed` method if a given request allowed or not."""

    def __init__(self, manager, matcher):
        self.manager = manager
        self.matcher = matcher

    def is_allowed(self, request):
        """Is given request intent allowed or not?"""
        policies = self.manager.find_by_request(request)
        if not policies or len(policies) == 0:
            return False
        else:
            return self._check_policies_allow(request, policies)

    def _check_policies_allow(self, request, policies):
        """Check if any of a given policy allows a specified request"""
        allow = False
        for p in policies:
            # First we check if action is OK. Since usually action is the most used check.
            match = self.matcher.matches(p, p.actions, request.action)
            if not match:
                continue
            # Subject is more performant check then resources, so we try it second.
            match = self.matcher.matches(p, p.subjects, request.subject)
            if not match:
                continue
            match = self.matcher.matches(p, p.resources, request.resource)
            if not match:
                continue
            if not self._check_conditions_pass(p, request):
                continue
            if not p.allow_access:
                return False
            allow = True
        return allow

    def _check_conditions_pass(self, policy, request):
        """Check conditions pass for a request"""
        for key, condition in enumerate(policy.conditions):
            try:
                ctx_condition = request.context[key]
            except KeyError:
                return False
            if not condition.satisfied(ctx_condition, request):
                return False
        return True
