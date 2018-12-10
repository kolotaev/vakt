"""
Namespace for a basic Policy class.
"""

import logging

from .effects import ALLOW_ACCESS, DENY_ACCESS
from .exceptions import PolicyCreationError
from .util import JsonSerializer, PrettyPrint
from .rules.base import Rule
from . import TYPE_STRINGS, TYPE_ATTRIBUTES


log = logging.getLogger(__name__)


class Policy(JsonSerializer, PrettyPrint):
    """Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of rules.
    """
    def __init__(self, uid, subjects=(), effect=DENY_ACCESS, resources=(), actions=(), rules=None, description=None):
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
        self.type = self.get_type()

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
        if 'type' in props:
            del props['type']
        return cls(**props)

    def allow_access(self):
        """Does policy imply allow-access?"""
        return self.effect == ALLOW_ACCESS

    @property
    def start_tag(self):
        """Policy expression start tag"""
        return '<'

    @property
    def end_tag(self):
        """Policy expression end tag"""
        return '>'

    def get_type(self):
        for elements in [self.resources, self.actions, self.subjects]:
            if any([isinstance(e, Rule) for e in elements]):
                return TYPE_ATTRIBUTES
        return TYPE_STRINGS
