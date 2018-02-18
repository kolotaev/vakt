import re
import logging

from ..conditions.base import Condition


log = logging.getLogger(__name__)


class StringEqualCondition(Condition):
    """Condition that is satisfied if the string value equals the specified property of this condition"""

    def __init__(self, equals):
        if not isinstance(equals, str):
            log.error('StringEqualCondition creation. Equals property should be a string')
            raise TypeError('equals property should be a string')
        self.equals = equals

    def satisfied(self, what, request=None):
        return isinstance(what, str) and what == self.equals


class StringPairsEqualCondition(Condition):
    """Condition that is satisfied when given data is an array of pairs and
       those pairs are represented by equal to each other strings"""

    def satisfied(self, what, request=None):
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


class RegexMatchCondition(Condition):
    """Condition that is satisfied when given data matches the provided regular expression.
       Note, that you should provide syntactically valid regular-expression string."""

    def __init__(self, pattern):
        try:
            # todo - de we need escape?
            self.regex = re.compile(pattern)
        except Exception as e:
            log.error('RegexMatchCondition creation. Failed to compile regexp %s', pattern)
            raise TypeError('pattern should be a valid regexp string. Error %s' % e)

    def satisfied(self, what, request=None):
        return bool(self.regex.match(str(what)))
