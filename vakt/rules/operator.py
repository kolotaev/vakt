"""
All Rules that are related to comparison operators:
==, !=, <, >, <=, >=
They behave the same as you might expect from Python comparison operators.
"""

import logging
from abc import ABCMeta

from ..rules.base import Rule


log = logging.getLogger(__name__)


__all__ = [
    'Eq',
    'NotEq',
    'Greater',
    'Less',
    'GreaterOrEqual',
    'LessOrEqual'
]


class OperatorRule(Rule, metaclass=ABCMeta):
    """
    Base class for all Logic Operator Rules
    """
    def __init__(self, val):
        self.val = val


class Eq(OperatorRule):
    """
    Rule that is satisfied when two values are equal '=='.
    For example: context={'referralCount': Eq(90)}
    """
    def satisfied(self, what, inquiry=None):
        if isinstance(self.val, tuple):
            val = list(self.val)
        else:
            val = self.val
        return val == what


class NotEq(OperatorRule):
    """
    Rule that is satisfied when two values are not equal '!='.
    For example: subjects=[{'stars': NotEq(100)}]
    """
    def satisfied(self, what, inquiry=None):
        if isinstance(self.val, tuple):
            val = list(self.val)
        else:
            val = self.val
        return val != what


class Greater(OperatorRule):
    """
    Rule that is satisfied when 'what' is greater '>' than initial value.
    For example: subjects=[{'stars': Greater(100)}]
    """
    def satisfied(self, what, inquiry=None):
        return what > self.val


class Less(OperatorRule):
    """
    Rule that is satisfied when 'what' is less '<' than initial value.
    For example: subjects=[{'stars': Less(100)}]
    """
    def satisfied(self, what, inquiry=None):
        return what < self.val


class GreaterOrEqual(OperatorRule):
    """
    Rule that is satisfied when 'what' is greater or equal '>=' than initial value.
    For example: subjects=[{'stars': GreaterOrEqual(100), 'name': Eq('Jason')}]
    """
    def satisfied(self, what, inquiry=None):
        return what >= self.val


class LessOrEqual(OperatorRule):
    """
    Rule that is satisfied when 'what' is less or equal '<=' than initial value.
    For example: subjects=[{'stars': LessOrEqual(100), 'name': Eq('Jason')}]
    """
    def satisfied(self, what, inquiry=None):
        return what <= self.val
