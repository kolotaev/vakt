"""
All Rules relevant to contexts that work with strings.
It may be subject, object, etc.
"""

import re
import logging
import warnings
from abc import ABCMeta

from ..rules.base import Rule


log = logging.getLogger(__name__)


__all__ = [
    'Equal',
    'PairsEqual',
    'RegexMatch',
    'StartsWith',
    'EndsWith',
    'Contains'
]


class Equal(Rule):
    """
    Rule that is satisfied if the string value equals the specified property of this rule.
    Performs case-sensitive and case-sensitive comparisons (based on `case_insensitive` flag).
    For example: context={'country': Equal('Mozambique', True)}
    """
    def __init__(self, val, case_insensitive=False):
        if not isinstance(val, str):
            log.error('%s creation. Initial property should be a string', type(self).__name__)
            raise TypeError('Initial property should be a string')
        self.val = val
        self.ci = case_insensitive

    def satisfied(self, what, inquiry=None):
        if isinstance(what, str):
            if self.ci:
                return what.lower() == self.val.lower()
            else:
                return what == self.val
        return False


class PairsEqual(Rule):
    """
    Rule that is satisfied when given data is an array of pairs and
    those pairs are represented by equal to each other strings.
    For example: context={'users': PairsEqual()}
    """
    def satisfied(self, what, inquiry=None):
        if not isinstance(what, list):
            return False
        for pair in what:
            if len(pair) != 2:
                return False
            if not isinstance(pair[0], str) and not isinstance(pair[1], str):
                return False
            if pair[0] != pair[1]:
                return False
        return True


class RegexMatch(Rule):
    """
    Rule that is satisfied when given data matches the provided regular expression.
    Note, that you should provide syntactically valid regular-expression string.
    For example: context={'file': RegexMatch(r'\.(rb|sh|py|ex)$')}
    """
    def __init__(self, pattern):
        try:
            self.regex = re.compile(pattern)
        except Exception as e:
            log.exception('%s creation. Failed to compile regexp %s', type(self).__name__, pattern)
            raise TypeError('pattern should be a valid regexp string. Error %s' % e)

    def satisfied(self, what, inquiry=None):
        return bool(self.regex.match(str(what)))


class SubstringRule(Rule, metaclass=ABCMeta):
    """
    Rule that is a base class for different substring-related rules.
    """
    def __init__(self, val):
        if not isinstance(val, str):
            log.error('%s creation. Initial property should be a string', type(self).__name__)
            raise TypeError('Initial property should be a string')
        self.val = val


class StartsWith(SubstringRule):
    """
    Rule that is satisfied when given string starts with initially provided substring.
    For example: context={'file': StartsWith('Route-')}
    """
    def satisfied(self, what, inquiry=None):
        if isinstance(what, str):
            return what.startswith(self.val)
        return False


class EndsWith(SubstringRule):
    """
    Rule that is satisfied when given string ends with initially provided substring.
    For example: context={'file': EndsWith('.txt')}
    """
    def satisfied(self, what, inquiry=None):
        if isinstance(what, str):
            return what.endswith(self.val)
        return False


class Contains(SubstringRule):
    """
    Rule that is satisfied when given string contains initially provided substring.
    For example: context={'file': Contains('sun')}
    """
    def satisfied(self, what, inquiry=None):
        if isinstance(what, str):
            return self.val in what
        return False


# Classes marked for removal in next releases
class StringEqualRule(Equal):
    def __init__(self, *args, **kwargs):
        warnings.warn('StringEqualRule will be removed in version 2.0. Use Equal', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)


class RegexMatchRule(RegexMatch):
    def __init__(self, *args, **kwargs):
        warnings.warn('RegexMatchRule will be removed in version 2.0. Use RegexMatch', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)


class StringPairsEqualRule(PairsEqual):
    def __init__(self, *args, **kwargs):
        warnings.warn('StringPairsEqualRule will be removed in version 2.0. Use PairsEqual',
                      DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)
