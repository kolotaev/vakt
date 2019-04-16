"""
All Rules that are related to logic and composition:
and, or, not, is-true, is-false.
"""

import logging
from abc import ABCMeta, abstractmethod

from ..rules.base import Rule


log = logging.getLogger(__name__)


__all__ = [
    'IsTrue',
    'IsFalse',
    'And',
    'Or',
    'Not',
    'Any',
    'Neither',
]


class BooleanRule(Rule, metaclass=ABCMeta):
    """
    Boolean Rule that is satisfied when 'what' is evaluated to a boolean true/false.
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
    """
    Rule that is satisfied when 'what' is evaluated to a boolean 'true'.
    For example: subject={'role': IsTrue(user.is_admin()), 'name': Eq('Jimmy')}
    """
    @property
    def val(self):
        return True


class IsFalse(BooleanRule):
    """
    Rule that is satisfied when 'what' is evaluated to a boolean 'false'.
    For example: subject={'role': IsFalse(user.is_admin()), 'name': Eq('Jimmy')}
    """
    @property
    def val(self):
        return False


class CompositionRule(Rule, metaclass=ABCMeta):
    """
    Abstract Rule that encompasses other Rules.
    """
    def __init__(self, *rules):
        for r in rules:
            if not isinstance(r, Rule):
                log.error("%s creation. Arguments should be of Rule class or it's derivatives", type(self).__name__)
                raise TypeError("Arguments should be of Rule class or it's derivatives")
        self.rules = rules


class And(CompositionRule):
    """
    Rule that is satisfied when all the rules it's composed of are satisfied.
    For example: subject={'stars': And(Greater(50), Less(120)), 'name': Eq('Jimmy')}
    """
    def satisfied(self, what, inquiry=None):
        answers = [x.satisfied(what, inquiry) for x in self.rules]
        return len(answers) > 0 and all(answers)


class Or(CompositionRule):
    """
    Rule that is satisfied when at least one of the rules it's composed of is satisfied.
    Uses short-circuit evaluation.
    For example: subject={'stars': Or(Greater(50), Less(120)), 'name': Eq('Jimmy')}
    """
    def satisfied(self, what, inquiry=None):
        for rule in self.rules:
            if rule.satisfied(what, inquiry):
                return True
        return False


class Not(Rule):
    """
    Rule that negates another Rule.
    For example: subject={'stars': Eq(555), 'name': Not(Eq('Jimmy'))}
    """
    def __init__(self, rule):
        if not isinstance(rule, Rule):
            log.error("%s creation. Arguments should be of Rule class or it's derivatives", type(self).__name__)
            raise TypeError("Arguments should be of Rule class or it's derivatives")
        self.rule = rule

    def satisfied(self, what, inquiry):
        return not self.rule.satisfied(what, inquiry)


class Any(Rule):
    """
    Rule that is always satisfied.
    For example: resource={'endpoint': Any(), 'method': Eq('POST')}
    """

    def satisfied(self, what=None, inquiry=None):
        return True


class Neither(Rule):
    """
    Rule that always isn't satisfied.
    For example: resource={'endpoint': Neither(), 'method': Eq('GET')}
    """

    def satisfied(self, what=None, inquiry=None):
        return False
