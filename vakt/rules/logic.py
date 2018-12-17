"""
All Rules that are related to logic:
Simple operator comparisons:
==, !=, <, >, <=, >=
They behave the same as you might expect from Python comparison operators.
"""

import logging

from ..rules.base import Rule

log = logging.getLogger(__name__)


class Eq(Rule):
    """Rule that is satisfied when two values are equal '=='"""
    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        if isinstance(self.val, tuple):
            val = list(self.val)
        else:
            val = self.val
        return val == what


class NotEq(Rule):
    """Rule that is satisfied when two values are not equal '!='"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        if isinstance(self.val, tuple):
            val = list(self.val)
        else:
            val = self.val
        return val != what


class Greater(Rule):
    """Rule that is satisfied when 'what' is greater '>' than initial value"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        if isinstance(what, tuple) and isinstance(what, tuple):
            return list(what) > list(self.val)
        return what > self.val


class Less(Rule):
    """Rule that is satisfied when 'what' is less '<' than initial value"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        if isinstance(what, tuple) and isinstance(what, tuple):
            return list(what) < list(self.val)
        return what < self.val


class GreaterOrEqual(Rule):
    """Rule that is satisfied when 'what' is greater or equal '>=' than initial value"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        if isinstance(what, tuple) and isinstance(what, tuple):
            return list(what) >= list(self.val)
        return what >= self.val


class LessOrEqual(Rule):
    """Rule that is satisfied when 'what' is less or equal '<=' than initial value"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        if isinstance(what, tuple) and isinstance(what, tuple):
            return list(what) <= list(self.val)
        return what <= self.val
