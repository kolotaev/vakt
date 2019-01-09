"""
All Rules relevant to contexts that work with strings.
It may be subject, object, etc.
"""

import re
import logging
import warnings

from ..rules.base import Rule


log = logging.getLogger(__name__)


class Equal(Rule):
    """
    Rule that is satisfied if the string value equals the specified property of this rule.
    Performs case-sensitive comparison.
    """
    def __init__(self, val):
        if not isinstance(val, str):
            log.error('%s creation. Initial property should be a string', type(self).__name__)
            raise TypeError('Initial property should be a string')
        self.val = val

    def satisfied(self, what, inquiry=None):
        return isinstance(what, str) and what == self.val


class EqualInsensitive(Rule):
    """
    Rule that is satisfied if the string value equals the specified property of this rule.
    Performs case-insensitive comparison.
    """
    def __init__(self, val):
        if not isinstance(val, str):
            log.error('%s creation. Initial property should be a string', type(self).__name__)
            raise TypeError('Initial property should be a string')
        self.val = val

    def satisfied(self, what, inquiry=None):
        return isinstance(what, str) and what.lower() == self.val.lower()


class PairsEqual(Rule):
    """Rule that is satisfied when given data is an array of pairs and
       those pairs are represented by equal to each other strings"""

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
    """Rule that is satisfied when given data matches the provided regular expression.
       Note, that you should provide syntactically valid regular-expression string."""

    def __init__(self, pattern):
        try:
            self.regex = re.compile(pattern)
        except Exception as e:
            log.exception('%s creation. Failed to compile regexp %s', type(self).__name__, pattern)
            raise TypeError('pattern should be a valid regexp string. Error %s' % e)

    def satisfied(self, what, inquiry=None):
        return bool(self.regex.match(str(what)))


# Classes marked for removal in next releases
class StringEqualRule(Equal):
    warnings.warn('StringEqualRule will be removed in version 2.0. Use Equal', DeprecationWarning, stacklevel=2)


class RegexMatchRule(RegexMatch):
    warnings.warn('RegexMatchRule will be removed in version 2.0. Use RegexMatch', DeprecationWarning, stacklevel=2)


class StringPairsEqualRule(PairsEqual):
    warnings.warn('StringPairsEqualRule will be removed in version 2.0. Use PairsEqual',
                  DeprecationWarning, stacklevel=2)
