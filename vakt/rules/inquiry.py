"""
All Rules relevant to Inquiry context
"""
import warnings

from ..rules.base import Rule

__all__ = [
    'SubjectEqual',
    'ActionEqual',
    'ResourceIn',
]


class SubjectEqual(Rule):
    """
    Rule that is satisfied if the string value equals the Inquiry's Subject.
    For example: context={'user': SubjectEqual()}
    This is an old Rule. Most often operator Rules will be enough.
    """
    def satisfied(self, what, inquiry=None):
        return inquiry and isinstance(what, str) and what == inquiry.subject


class ActionEqual(Rule):
    """
    Rule that is satisfied if the string value equals the Inquiry's Action.
    For example: context={'user': ActionEqual()}
    This is an old Rule. Most often operator Rules will be enough.
    """
    def satisfied(self, what, inquiry=None):
        return inquiry and isinstance(what, str) and what == inquiry.action


class ResourceIn(Rule):
    """
    Rule that is satisfied if list contains the Inquiry's Resource.
    For example: context={'user': ResourceIn()}
    This is an old Rule. Most often list Rules will be enough.
    """
    def satisfied(self, what, inquiry=None):
        return inquiry and isinstance(what, list) and inquiry.resource in what


# Classes marked for removal in next releases
class SubjectEqualRule(SubjectEqual):
    """Deprecated in favor of SubjectEqual"""
    def __init__(self, *args, **kwargs):
        warnings.warn('SubjectEqualRule will be removed in version 2.0. Use SubjectEqual',
                      DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)


class ActionEqualRule(ActionEqual):
    """Deprecated in favor of ActionEqual"""
    def __init__(self, *args, **kwargs):
        warnings.warn('ActionEqualRule will be removed in version 2.0. Use ActionEqual',
                      DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)


class ResourceInRule(ResourceIn):
    """Deprecated in favor of ResourceIn"""
    def __init__(self, *args, **kwargs):
        warnings.warn('ResourceInRule will be removed in version 2.0. Use ResourceIn',
                      DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)
