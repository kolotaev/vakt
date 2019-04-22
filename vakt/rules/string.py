"""
All Rules that work with strings.
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


class StringRule(Rule, metaclass=ABCMeta):
    """
    Basic Rule for strings
    """
    def __init__(self, val, ci=False):
        if not isinstance(val, str):
            log.error('%s creation. Initial property should be a string', type(self).__name__)
            raise TypeError('Initial property should be a string')
        self.val = val
        self.ci = ci


class Equal(StringRule):
    """
    Rule that is satisfied if the string value equals the specified property of this rule.
    Performs case-sensitive and case-sensitive comparisons (based on `ci` (case_insensitive) flag).
    For example: context={'country': Equal('Mozambique', True)}
    """
    def satisfied(self, what, inquiry=None):
        if isinstance(what, str):
            if self.ci:
                return what.lower() == self.val.lower()
            return what == self.val
        return False


class PairsEqual(Rule):
    """
    Rule that is satisfied when given data is an array of pairs and
    those pairs are represented by equal to each other strings.
    For example: context={'scores': PairsEqual()}
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
    r"""
    Rule that is satisfied when given data matches the provided regular expression.
    Note, that you should provide syntactically valid regular-expression string.
    For example: context={'file': RegexMatch(r'\.(rb|sh|py|exe)$')}
    """
    def __init__(self, pattern):
        try:
            self.regex = re.compile(pattern)
        except Exception as e:
            log.exception('%s creation. Failed to compile regexp %s', type(self).__name__, pattern)
            raise TypeError('pattern should be a valid regexp string. Error %s' % e)

    def satisfied(self, what, inquiry=None):
        return bool(self.regex.match(str(what)))


class StartsWith(StringRule):
    """
    Rule that is satisfied when given string starts with initially provided substring.
    For example: context={'file': StartsWith('Route-', ci=True)}
    """
    def satisfied(self, what, inquiry=None):
        if isinstance(what, str):
            if self.ci:
                return what.lower().startswith(self.val.lower())
            return what.startswith(self.val)
        return False


class EndsWith(StringRule):
    """
    Rule that is satisfied when given string ends with initially provided substring.
    For example: context={'file': EndsWith('.txt')}
    """
    def satisfied(self, what, inquiry=None):
        if isinstance(what, str):
            if self.ci:
                return what.lower().endswith(self.val.lower())
            return what.endswith(self.val)
        return False


class Contains(StringRule):
    """
    Rule that is satisfied when given string contains initially provided substring.
    For example: context={'file': Contains('sun')}
    """
    def satisfied(self, what, inquiry=None):
        if isinstance(what, str):
            if self.ci:
                return self.val.lower() in what.lower()
            return self.val in what
        return False


# Classes marked for removal in next releases
class StringEqualRule(Equal):
    """Deprecated in favor of Equal"""
    def __init__(self, *args, **kwargs):
        warnings.warn('StringEqualRule will be removed in version 2.0. Use Equal', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)


class RegexMatchRule(RegexMatch):
    """Deprecated in favor of RegexMatch"""
    def __init__(self, *args, **kwargs):
        warnings.warn('RegexMatchRule will be removed in version 2.0. Use RegexMatch', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)


class StringPairsEqualRule(PairsEqual):
    """Deprecated in favor of PairsEqual"""
    def __init__(self, *args, **kwargs):
        warnings.warn('StringPairsEqualRule will be removed in version 2.0. Use PairsEqual',
                      DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)
