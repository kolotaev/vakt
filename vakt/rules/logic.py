"""
All Rules that are related to logic:
Simple operator comparisons:
==, !=, <, >, <=, >=
They behave the same as you might expect from Python comparison operators.
"""

import logging
from abc import ABCMeta, abstractmethod

from ..rules.base import Rule

log = logging.getLogger(__name__)


class OperatorRule(Rule, metaclass=ABCMeta):
    """
    Base class for all Logic Operator Rules
    """
    def __init__(self, val):
        super().__init__()
        self.val = val


class Eq(OperatorRule):
    """Rule that is satisfied when two values are equal '=='"""
    def satisfied(self, what, inquiry=None):
        if isinstance(self.val, tuple):
            val = list(self.val)
        else:
            val = self.val
        return val == what


class NotEq(OperatorRule):
    """Rule that is satisfied when two values are not equal '!='"""
    def satisfied(self, what, inquiry=None):
        if isinstance(self.val, tuple):
            val = list(self.val)
        else:
            val = self.val
        return val != what


class Greater(OperatorRule):
    """Rule that is satisfied when 'what' is greater '>' than initial value"""
    def satisfied(self, what, inquiry=None):
        if isinstance(what, tuple) and isinstance(what, tuple):
            return list(what) > list(self.val)
        return what > self.val


class Less(OperatorRule):
    """Rule that is satisfied when 'what' is less '<' than initial value"""
    def satisfied(self, what, inquiry=None):
        if isinstance(what, tuple) and isinstance(what, tuple):
            return list(what) < list(self.val)
        return what < self.val


class GreaterOrEqual(OperatorRule):
    """Rule that is satisfied when 'what' is greater or equal '>=' than initial value"""
    def satisfied(self, what, inquiry=None):
        if isinstance(what, tuple) and isinstance(what, tuple):
            return list(what) >= list(self.val)
        return what >= self.val


class LessOrEqual(OperatorRule):
    """Rule that is satisfied when 'what' is less or equal '<=' than initial value"""
    def satisfied(self, what, inquiry=None):
        if isinstance(what, tuple) and isinstance(what, tuple):
            return list(what) <= list(self.val)
        return what <= self.val


class BooleanRule(Rule, metaclass=ABCMeta):
    """
    Abstract Rule that is satisfied when 'what' is evaluated to a boolean 'true'/'false'.
    Its `satisfied` accepts:
     - a callable without arguments
     - non-callable
     - expressions
    """
    def satisfied(self, what, inquiry=None):
        res = what() if callable(what) else what
        return bool(res) == self.val

    @property
    @abstractmethod
    def val(self):
        pass


class IsTrue(BooleanRule):
    """Rule that is satisfied when 'what' is evaluated to a boolean 'true'."""
    @property
    def val(self):
        return True


class IsFalse(BooleanRule):
    """Rule that is satisfied when 'what' is evaluated to a boolean 'false'."""
    @property
    def val(self):
        return False
