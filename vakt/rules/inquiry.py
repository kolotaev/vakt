"""
All Rules relevant to Inquiry context
"""

from ..rules.base import Rule


class SubjectEqualRule(Rule):
    """Rule that is satisfied if the string value equals the Inquiry's Subject"""

    def satisfied(self, what, inquiry):
        return isinstance(what, str) and what == inquiry.subject


class ActionEqualRule(Rule):
    """Rule that is satisfied if the string value equals the Inquiry's Action"""

    def satisfied(self, what, inquiry):
        return isinstance(what, str) and what == inquiry.action


class ResourceInRule(Rule):
    """Rule that is satisfied if list contains the Inquiry's Resource"""

    def satisfied(self, what, inquiry):
        return isinstance(what, list) and inquiry.resource in what
