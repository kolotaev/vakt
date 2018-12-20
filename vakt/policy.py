"""
Namespace for a basic Policy class.
"""

import logging
import warnings

from .effects import ALLOW_ACCESS, DENY_ACCESS
from .exceptions import PolicyCreationError
from .util import JsonSerializer, PrettyPrint
from .rules.base import Rule
from . import TYPE_STRING_BASED, TYPE_RULE_BASED


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
        self.type = None

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

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        # always calculate type. Evn if type is set explicitly. Dict assign eliminates recursion
        self.__dict__['type'] = self._calculate_type()

    def _calculate_type(self):
        fields = ['subjects', 'resources', 'actions']
        for elements in [getattr(self, f, ()) for f in fields]:
            if any([isinstance(e, Rule) for e in elements]):
                return TYPE_RULE_BASED
        return TYPE_STRING_BASED
