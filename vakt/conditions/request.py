from vakt.conditions.base import Condition


class SubjectEqualCondition(Condition):
    """Condition that is fulfilled if the string value equals the Subject property in request"""

    def ok(self, what, request):
        return isinstance(what, str) and what == request.subject
