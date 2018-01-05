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
        self.resource = manager
        self.action = matcher

    def is_allowed(self, request):
        """Is given request intent allowed or not?"""
        pass
