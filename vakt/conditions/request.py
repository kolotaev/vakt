from ..conditions.base import Condition


class SubjectEqualCondition(Condition):
    """Condition that is satisfied if the string value equals the Subject property in request"""

    def satisfied(self, what, request):
        return isinstance(what, str) and what == request.subject
