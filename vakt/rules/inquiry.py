"""
All Rules relevant to Inquiry context
"""
import warnings

from ..rules.base import Rule


class SubjectEqual(Rule):
    """Rule that is satisfied if the string value equals the Inquiry's Subject"""
    def satisfied(self, what, inquiry):
        return isinstance(what, str) and what == inquiry.subject


class ActionEqual(Rule):
    """Rule that is satisfied if the string value equals the Inquiry's Action"""
    def satisfied(self, what, inquiry):
        return isinstance(what, str) and what == inquiry.action


class ResourceIn(Rule):
    """Rule that is satisfied if list contains the Inquiry's Resource"""
    def satisfied(self, what, inquiry):
        return isinstance(what, list) and inquiry.resource in what


# Classes marked for removal in next releases
class SubjectEqualRule(SubjectEqual):
    warnings.warn('SubjectEqualRule will be removed in version 2.0. Use SubjectEqual', DeprecationWarning, stacklevel=2)


class ActionEqualRule(ActionEqual):
    warnings.warn('ActionEqualRule will be removed in version 2.0. Use ActionEqual', DeprecationWarning, stacklevel=2)


class ResourceInRule(ResourceIn):
    warnings.warn('ResourceInRule will be removed in version 2.0. Use ResourceIn', DeprecationWarning, stacklevel=2)
