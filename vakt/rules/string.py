"""
All Rules relevant to contexts that work with strings.
It may be subject, object, etc.
"""

import re
import logging

from ..rules.base import Rule


log = logging.getLogger(__name__)


class StringEqualRule(Rule):
    """Rule that is satisfied if the string value equals the specified property of this rule"""

    def __init__(self, val):
        if not isinstance(val, str):
            log.error('%s creation. Initial property should be a string', type(self).__name__)
            raise TypeError('Initial property should be a string')
        self.val = val

    def satisfied(self, what, inquiry=None):
        return isinstance(what, str) and what == self.val


class StringPairsEqualRule(Rule):
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


class RegexMatchRule(Rule):
    """Rule that is satisfied when given data matches the provided regular expression.
       Note, that you should provide syntactically valid regular-expression string."""

    def __init__(self, pattern):
        try:
            self.regex = re.compile(pattern)
        except Exception as e:
            log.error('%s creation. Failed to compile regexp %s', type(self).__name__, pattern)
            raise TypeError('pattern should be a valid regexp string. Error %s' % e)

    def satisfied(self, what, inquiry=None):
        return bool(self.regex.match(str(what)))
