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
        # todo
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


class LogicCompositionRule(Rule, metaclass=ABCMeta):
    """
    Abstract Rule that encompasses other Rules.
    """
    def __init__(self, *rules):
        for r in rules:
            if not isinstance(r, Rule):
                log.error("%s creation. Arguments should be of Rule class or it's derivatives", type(self).__name__)
                raise TypeError("Arguments should be of Rule class or it's derivatives")
        self.rules = rules


class And(LogicCompositionRule):
    """
    Rule that is satisfied when all the rules it's composed of are satisfied.
    """
    def satisfied(self, what, inquiry):
        answers = [x.satisfied(what, inquiry) for x in self.rules]
        return len(answers) > 0 and all(answers)


class Or(LogicCompositionRule):
    """
    Rule that is satisfied when at least one of the rules it's composed of is satisfied.
    Uses short-circuit evaluation.
    """
    def satisfied(self, what, inquiry):
        for rule in self.rules:
            if rule.satisfied(what, inquiry):
                return True
        return False


class Not(Rule):
    """
    Rule that negates another Rule.
    """
    def __init__(self, rule):
        if not isinstance(rule, Rule):
            log.error("%s creation. Arguments should be of Rule class or it's derivatives", type(self).__name__)
            raise TypeError("Arguments should be of Rule class or it's derivatives")
        self.rule = rule

    def satisfied(self, what, inquiry):
        return not self.rule.satisfied(what, inquiry)
