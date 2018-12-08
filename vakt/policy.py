"""
Namespace for a basic Policy class.
"""

import logging
from abc import ABCMeta, abstractmethod

from .effects import ALLOW_ACCESS, DENY_ACCESS
from .exceptions import PolicyCreationError
from .util import JsonSerializer, PrettyPrint
from .rules.base import Rule


log = logging.getLogger(__name__)

TYPE_REGEX = 0
TYPE_STRING = 1
TYPE_ATTRIBUTES = 2


class Policy:
    """
    Factory for creating Policies of various types based on the Policy properties.
    """
    def __call__(self, *args, **kwargs):
        try:
            return AttributesPolicy(args, kwargs)
        except PolicyCreationError:
            try:
                return RegexPolicy(args, kwargs)
            except PolicyCreationError:
                return StringPolicy(args, kwargs)


class BasePolicy(JsonSerializer, PrettyPrint, metaclass=ABCMeta):
    """Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of rules.
    """
    def __init__(self, uid, subjects=(), effect=DENY_ACCESS, resources=(), actions=(), rules=None, description=None):
        self.type = self.get_type()
        self._check_args(subjects, resources, actions)
        self.uid = uid
        self.subjects = subjects
        self.effect = effect or DENY_ACCESS
        self.resources = resources
        self.actions = actions
        rules = rules or {}
        if not isinstance(rules, dict):
            log.error('Error creating Policy. Rules must be a dictionary')
            raise PolicyCreationError("Error creating Policy. Rules must be a dictionary")
        self.rules = rules
        self.description = description

    @classmethod
    def from_json(cls, data):
        props = cls._parse(data)
        if 'uid' not in props:
            log.error("Error creating policy from json. 'uid' attribute is required")
            raise PolicyCreationError("Error creating policy from json. 'uid' attribute is required")
        rules = {}
        if 'rules' in props:
            for k, clazz in props['rules'].items():
                rules[k] = Rule.from_json(clazz)
        props['rules'] = rules
        return cls(**props)

    def allow_access(self):
        """Does policy imply allow-access?"""
        return self.effect == ALLOW_ACCESS

    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def _check_args(self, *args):
        pass


class RegexPolicy(BasePolicy):
    """
    Policy whose parts are defined in Regular Expression syntax
    """
    def get_type(self):
        return TYPE_REGEX

    def _check_args(self, *args):
        for a in args:
            for el in a:
                if self.start_tag not in el and self.end_tag not in el:
                    raise PolicyCreationError('RegexPolicy should have balanced policy tags')

    @property
    def start_tag(self):
        """Policy expression start tag"""
        return '<'

    @property
    def end_tag(self):
        """Policy expression end tag"""
        return '>'


class StringPolicy(BasePolicy):
    """
    Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of rules that are defined with strings
    """
    def get_type(self):
        return TYPE_STRING

    def _check_args(self):
        pass


class AttributesPolicy(BasePolicy):
    """
    Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of rules that are defined with attributes
    """
    def get_type(self):
        return TYPE_ATTRIBUTES

    def _check_args(self, *args):
        if not all(map(lambda x: isinstance(x, dict), args)):
            raise PolicyCreationError('AttributesPolicy should have elements defined with a dictionary')
        # if any([isinstance(a, dict) for a in [self.resource, self.action, self.subject]]):
        # return 0
