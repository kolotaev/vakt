"""
All Rules for defining Inquiry elements relations
"""
from abc import ABCMeta, abstractmethod

from ..rules.base import Rule


__all__ = [
    'SubjectEqual',
    'ActionEqual',
    'ResourceIn',
    'SubjectMatch',
    'ActionMatch',
    'ResourceMatch',
]


class InquiryMatchAbstract(Rule, metaclass=ABCMeta):
    """
    Base rule for concrete InquiryMatch rule implementations.
    """
    def __init__(self, attribute=None):
        self.attribute = attribute

    def satisfied(self, what, inquiry=None):
        if not inquiry:
            return False
        inquiry_value = getattr(inquiry, self._field_name())
        if self.attribute is not None:
            if isinstance(inquiry_value, dict) and self.attribute in inquiry_value:
                inquiry_value = inquiry_value[self.attribute]
            else:
                return False
        return what == inquiry_value

    @abstractmethod
    def _field_name(self):
        pass


class SubjectMatch(InquiryMatchAbstract):
    """
    Rule that is satisfied if the value equals the Inquiry's Subject or it's attribute.
    For example: resources=[SubjectMatch('nick')]
    """
    def _field_name(self):
        return 'subject'


class ActionMatch(InquiryMatchAbstract):
    """
    Rule that is satisfied if the value equals the Inquiry's Action or it's attribute.
    For example: resources=[{'ref': ActionMatch('ref_method')}]
    """
    def _field_name(self):
        return 'action'


class ResourceMatch(InquiryMatchAbstract):
    """
    Rule that is satisfied if the value equals the Inquiry's Resource or it's attribute.
    For example: resources=[ResourceMatch('sub-category')]
    """
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
