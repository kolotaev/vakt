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
        """Check if any of a given policy allow a specified request"""
        allow = False
        for p in policies:
            match = self.matcher.matches(p, p.actions, request.action)
            if not match:
                continue
