import re
import logging
from abc import ABCMeta, abstractmethod

from .compiler import compile_regex
from .exceptions import InvalidPatternError


log = logging.getLogger(__name__)


class RegexChecker:
    """
    Checker that uses regular expressions.
    E.g. 'Dog', 'Doge', 'Dogs' fit <Dog[se]?>
         'Dogger' doesn't fit <Dog[se]?>
    """

    def fits(self, policy, field, what):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where = getattr(policy, field, [])
        for i in where:
            if policy.start_tag not in i:  # check if 'where' item is written in a policy-defined-regex syntax.
                if i == what:  # it's a single string match
                    return True
                continue
            try:
                pattern = compile_regex(i, policy.start_tag, policy.end_tag)
            except InvalidPatternError:
                log.exception('Error matching policy, because of failed regex %s compilation', i)
                return False
            if re.match(pattern, what):
                return True
        return False


class StringChecker(metaclass=ABCMeta):
    """
    Checker that uses string equality.
    You have to redefine `compare` method.
    """

    def fits(self, policy, field, what):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where = getattr(policy, field, [])
        for item in where:
            if policy.start_tag == item[0] and policy.end_tag == item[-1]:
                item = item[1:-1]
            if self.compare(what, item):
                return True
            continue
        return False

    @abstractmethod
    def compare(self, needle, haystack):
        pass


class StringExactChecker(StringChecker):
    """
    Checker that uses exact string equality. Case-sensitive.
    E.g. 'sun' in 'sunny' - False
         'sun' in 'sun' - True
    """

    def compare(self, needle, haystack):
        return needle == haystack


class StringFuzzyChecker(StringChecker):
    """
    Checker that uses fuzzy substring equality. Case-sensitive.
    E.g. 'sun' in 'sunny' - True
         'sun' in 'sun' - True
    """

    def compare(self, needle, haystack):
        return needle in haystack
