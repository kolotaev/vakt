"""
All Rules relevant to Inquiry context
"""
import warnings
from abc import ABCMeta, abstractmethod

from ..rules.base import Rule
from ..rules import Eq

__all__ = [
    'SubjectEqual',
    'ActionEqual',
    'ResourceIn',
    'InquirySubjectMatch',
    'InquiryActionMatch',
    'InquiryResourceMatch',
]


class InquiryMatchAbstract(Rule, metaclass=ABCMeta):
    def __init__(self, attribute=None, rule_class=Eq):
        self.attribute = attribute
        self.rule_class = rule_class.__class__.__name__

    def satisfied(self, what, inquiry=None):
        if not inquiry:
            return False
        inquiry_value = getattr(inquiry, self._field_name())
        if self.attribute is not None:
            if isinstance(inquiry_value, dict) and self.attribute in inquiry_value:
                inquiry_value = inquiry_value[self.attribute]
            else:
                return False
        try:
            rule = self.rule_class.__new__(*inquiry_value)
            return rule.satisfied(what)
        except:
            return False

    @abstractmethod
    def _field_name(self):
        pass


class InquirySubjectMatch(InquiryMatchAbstract):
    def _field_name(self):
        return 'subject'


class InquiryActionMatch(InquiryMatchAbstract):
    def _field_name(self):
        return 'action'


class InquiryResourceMatch(InquiryMatchAbstract):
    def _field_name(self):
        return 'resource'


class SubjectEqual(Rule):
    """
    Rule that is satisfied if the string value equals the Inquiry's Subject.
    For example: context={'user': SubjectEqual()}
    This Rule only works for string-based policies.
    """
    def satisfied(self, what, inquiry=None):
        return inquiry and isinstance(what, str) and what == inquiry.subject


class ActionEqual(Rule):
    """
    Rule that is satisfied if the string value equals the Inquiry's Action.
    For example: context={'user': ActionEqual()}
    This Rule only works for string-based policies.
    """
    def satisfied(self, what, inquiry=None):
        return inquiry and isinstance(what, str) and what == inquiry.action


class ResourceIn(Rule):
    """
    Rule that is satisfied if list contains the Inquiry's Resource.
    For example: context={'user': ResourceIn()}
    This Rule only works for string-based policies.
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
