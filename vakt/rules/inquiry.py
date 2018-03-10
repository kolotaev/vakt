from ..rules.base import Rule


class SubjectEqualRule(Rule):
    """Rule that is satisfied if the string value equals the Subject property in inquiry"""

    def satisfied(self, what, inquiry):
        return isinstance(what, str) and what == inquiry.subject
