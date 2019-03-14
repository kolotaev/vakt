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
    def fits(self, policy, field, what):
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

    def fits(self, policy, field, what):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where = getattr(policy, field, [])
        for i in where:
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

    def fits(self, policy, field, what):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where = getattr(policy, field, [])
        for item in where:
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
    def fits(self, policy, field, what):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where_list = getattr(policy, field, [])
        for i in where_list:
            item_result = False
            if not isinstance(i, dict):
                continue  # if not dict, skip it - we are not meant to handle it
            for key, rule in i.items():
                try:
                    what_value = what[key]
                    item_result = rule.satisfied(what_value)
                # at least one missing key in inquiry's data means no match for this item
                except (KeyError, TypeError) as e:
                    # todo - add more specific handling
                    log.debug('Error matching Policy, because data has no key "%s" required by Policy' % key)
                    item_result = False
                # broad exception for possible custom exceptions. Any exception -> no match
                except Exception as e:
                    log.exception('Error matching Policy, because of raised exception', e)
                    item_result = False
                # at least one item's key didn't satisfy -> fail fast: policy doesn't fit anyway
                if not item_result:
                    break
            # If at least one item fits -> policy fits for this field
            if item_result:
                return True
        return False


class MixedChecker(Checker):
    """
    Checker that uses other Checkers that it's comprised of.
    Checks are performed in the order in which the Checkers were added to MixedChecker
    """
    def __init__(self, *checkers):
        if len(checkers) == 0:
            raise TypeError('Mixed Checker must be comprised of at least one Checker')
        for checker in checkers:
            if not isinstance(checker, Checker):
                raise TypeError('Mixed Checker can only be comprised of other Checkers, but %s given' % type(checker))
        self.checkers = checkers

    def fits(self, policy, field, what):
        for checker in self.checkers:
            try:
                result = checker.fits(policy, field, what)
            # Use broad exception to prevent unknown exceptions in custom checkers
            except Exception:
                result = False
            if result:
                return True
        return False
