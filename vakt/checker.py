"""
Module for various checkers.
"""

import re
import logging
from functools import lru_cache
from abc import ABCMeta, abstractmethod

from .parser import compile_regex
from .exceptions import InvalidPatternError


log = logging.getLogger(__name__)


class Checker(metaclass=ABCMeta):
    """
    Abstract class for Checker typing.
    """
    @abstractmethod
    def fits(self, policy, field, what, inquiry=None):
        """
        Check if fields from Inquiry fit some Policies
        """
        pass


class RegexChecker(Checker):
    """
    Checker that uses regular expressions.
    E.g. 'Dog', 'Doge', 'Dogs' fit <Dog[se]?>
         'Dogger' doesn't fit <Dog[se]?>
    """

    def __init__(self, cache_size=1024):
        """Set up LRU-cache size for compiled regular expressions."""
        self.compile = lru_cache(maxsize=cache_size)(compile_regex)

    def fits(self, policy, field, what, inquiry=None):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where = getattr(policy, field, [])
        for i in where:
            # We are not meant to handle non-string values if they accidentally got here
            if type(i) != str:
                continue
            # check if 'where' item is not written in a policy-defined-regex syntax.
            if policy.start_tag not in i and policy.end_tag not in i:
                if i != what:
                    continue       # continue if it's not a string match
                else:
                    return True    # we've found a string match - policy fits by simple string value
            try:
                pattern = self.compile(i, policy.start_tag, policy.end_tag)
            except InvalidPatternError:
                log.exception('Error matching policy, because of failed regex %s compilation', i)
                return False
            if re.match(pattern, what):
                return True
        return False


class StringChecker(Checker):
    """
    Checker that uses string equality.
    You have to redefine `compare` method.
    """

    def fits(self, policy, field, what, inquiry=None):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where = getattr(policy, field, [])
        for item in where:
            # We are not meant to handle non-string values if they accidentally got here
            if type(item) != str:
                continue
            if policy.start_tag == item[0] and policy.end_tag == item[-1]:
                item = item[1:-1]
            if self.compare(what, item):
                return True
        return False

    @abstractmethod
    def compare(self, needle, haystack):
        """Compares two string values. Override it in a subclass"""
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
         'sun' in 'unsung' - True
         'sun' in 'sun' - True
    """

    def compare(self, needle, haystack):
        return needle in haystack


class RulesChecker(Checker):
    """
    Checker that uses Rules defined inside dictionaries to determine match.
    """
    def fits(self, policy, field, what, inquiry=None):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where_list = getattr(policy, field, [])
        is_what_dict = isinstance(what, dict)
        for i in where_list:
            item_result = False
            # If not dict or Rule, skip it - we are not meant to handle it.
            # Do not use isinstance for higher execution speed
            if type(i) == dict:
                for key, rule in i.items():
                    if not is_what_dict:
                        log.debug('Error matching Policy: data %r in Inquiry is not `dict`', what)
                        item_result = False
                    # at least one missing key in inquiry's data means no match for this item
                    elif key not in what:
                        log.debug('Error matching Policy: data %r has no key "%r" required by Policy', what, key)
                        item_result = False
                    else:
                        what_value = what[key]
                        item_result = self._check_satisfied(rule, what_value, inquiry)
                    # at least one item's key didn't satisfy -> fail fast: policy doesn't fit anyway
                    if not item_result:
                        break
            elif callable(getattr(i, 'satisfied', '')):
                item_result = self._check_satisfied(i, what, inquiry)
            # If at least one item fits -> policy fits for this field
            if item_result:
                return True
        return False

    @staticmethod
    def _check_satisfied(rule, what_value, inquiry=None):
        try:
            return rule.satisfied(what_value, inquiry)
        # broad exception for possible custom exceptions. Any exception -> no match
        # todo - decide on granular handler
        except Exception:
            log.exception('Error matching Policy, because of raised exception')
            return False
