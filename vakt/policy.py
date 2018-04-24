"""
Namespace for a basic Policy class.
"""

import logging

from .effects import ALLOW_ACCESS, DENY_ACCESS
from .exceptions import PolicyCreationError
from .util import JsonDumper, PrettyPrint
from .rules.base import Rule


log = logging.getLogger(__name__)


class Policy(JsonDumper, PrettyPrint):
    """Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of rules."""

    def __init__(self, uid, description=None, subjects=(), effect=DENY_ACCESS, resources=(), actions=(), rules=None):
        self.uid = uid
        self.description = description
        self.subjects = subjects
        self.effect = effect or DENY_ACCESS
        self.resources = resources
        self.actions = actions
        rules = rules or {}
        if not isinstance(rules, dict):
            log.exception('Error creating Policy. Rules must be a dictionary')
            raise PolicyCreationError("Error creating Policy. Rules must be a dictionary")
        self.rules = rules

    @classmethod
    def from_json(cls, data):
        props = cls._parse(data)
        if 'uid' not in props:
            log.exception("Error creating policy from json. 'uid' attribute is required")
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

    @property
    def start_tag(self):
        """Policy expression start tag"""
        return '<'

    @property
    def end_tag(self):
        """Policy expression end tag"""
        return '>'
