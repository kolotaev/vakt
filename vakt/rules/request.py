from ..rules.base import Rule


class SubjectEqualRule(Rule):
    """Rule that is satisfied if the string value equals the Subject property in request"""

    def satisfied(self, what, request):
        return isinstance(what, str) and what == request.subject
