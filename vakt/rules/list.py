"""
All Rules relevant to list-related context.

Initial list against which the search will be performed is cast to a Set to speed-up further search operations.
Consequently beware that it may be slow on data insertion for large lists.

For some of the checks where list is an input (e.g. AllIn, AllNotIn, ...)
cast of input to Set is also performed.

Various search options are available:
- is item in list?
- is not item in the list?
- are all the items in the list?
- are all the items not in the list?
- is at least one of the provided items in the list?
- is at least one of the provided items not in the list?
"""

import logging
from abc import abstractmethod

from ..rules.base import Rule

log = logging.getLogger(__name__)


class ListRule(Rule):
    """
    Generic Rule for List-related checks
    """
    def __init__(self, data):
        if not isinstance(data, list):
            log.error('%s creation. Initial data should be of list type', type(self).__name__)
            raise TypeError('Initial data should be of list type')
        self.data = set(data)

    @abstractmethod
    def satisfied(self, what, inquiry=None):
        pass


class In(ListRule):
    """
    Is item in list?
    For example: action={'method': In('read', 'write', 'delete')}
    """
    def satisfied(self, what, inquiry=None):
        return _one_in_list(what, self.data)


class NotIn(ListRule):
    """
    Is not item in the list?
    For example: action={'method': NotIn('read', 'write', 'delete')}
    """
    def satisfied(self, what, inquiry=None):
        return not _one_in_list(what, self.data)


class AllIn(ListRule):
    """
    Are all the items in the list?
    For example: action={'methods': AllIn('read', 'write', 'delete')}
    """
    def satisfied(self, what, inquiry=None):
        if not isinstance(what, list):
            raise TypeError('Value should be of list type')
        return _all_in_list(what, self.data)


class AllNotIn(ListRule):
    """
    Are all the items not in the list?
    For example: action={'methods': AllNotIn('read', 'write', 'delete')}
    """
    def satisfied(self, what, inquiry=None):
        if not isinstance(what, list):
            raise TypeError('Value should be of list type')
        return not _all_in_list(what, self.data)


class AnyIn(ListRule):
    """
    Are any of the items in the list?
    For example: action={'methods': AnyIn('read', 'write', 'delete')}
    """
    def satisfied(self, what, inquiry=None):
        if not isinstance(what, list):
            raise TypeError('Value should be of list type')
        return _any_in_list(what, self.data)


class AnyNotIn(ListRule):
    """
    Are any of the items not in the list?
    For example: action={'methods': AnyNotIn('read', 'write', 'delete')}
    """
    def satisfied(self, what, inquiry=None):
        if not isinstance(what, list):
            raise TypeError('Value should be of list type')
        return bool(set(what).difference(self.data))


def _one_in_list(what, data):
    return what in data


def _all_in_list(what, data):
    return set(what).issubset(data)


def _any_in_list(what, data):
    return bool(data.intersection(set(what)))
