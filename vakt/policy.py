"""
Namespace for a basic Policy class.
"""

import logging
import warnings

from .effects import ALLOW_ACCESS, DENY_ACCESS
from .exceptions import PolicyCreationError
from .util import JsonSerializer, PrettyPrint
from .rules.base import Rule
from . import TYPE_STRINGS, TYPE_ATTRIBUTES


log = logging.getLogger(__name__)


class Policy(JsonSerializer, PrettyPrint):
    """Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of context restrictions.
    """
    def __init__(self, uid, subjects=(), effect=DENY_ACCESS, resources=(),
                 actions=(), context=None, rules=None, description=None):
        self.uid = uid
        self.subjects = subjects
        self.effect = effect or DENY_ACCESS
        self.resources = resources
        self.actions = actions
        # check for deprecated rules argument.
        # If both 'context' and 'rules' are present - 'context' wins
        if context:
            pass
        elif rules:
            warnings.warn("'rules' argument will be removed in next version. Use 'context' argument",
                          DeprecationWarning, stacklevel=2)
            context = rules
        else:
            context = {}
        if not isinstance(context, dict):
            log.error('Error creating Policy. Context must be a dictionary')
            raise PolicyCreationError("Error creating Policy. Context must be a dictionary")
        self.context = context
        self.description = description
        self.type = self.get_type()

    @classmethod
    def from_json(cls, data):
        props = cls._parse(data)
        if 'uid' not in props:
            log.error("Error creating policy from json. 'uid' attribute is required")
            raise PolicyCreationError("Error creating policy from json. 'uid' attribute is required")
        context_rules = {}
        if 'context' in props:
            rules = props['context']
        elif 'rules' in props:  # this is to support deprecated 'rules' attribute
            rules = props['rules']
        else:
            rules = {}
        for k, clazz in rules.items():
            context_rules[k] = Rule.from_json(clazz)
        props['context'] = context_rules
        if 'type' in props:  # type is calculated dynamically on init
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
