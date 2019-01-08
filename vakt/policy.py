"""
Namespace for a basic Policy class.
"""

import logging
import warnings

from .effects import ALLOW_ACCESS, DENY_ACCESS
from .exceptions import PolicyCreationError
from .util import JsonSerializer, PrettyPrint
from . import TYPE_STRING_BASED, TYPE_RULE_BASED


log = logging.getLogger(__name__)


class Policy(JsonSerializer, PrettyPrint):
    """Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of context restrictions.
    """

    # Fields that affect Policy definition and further logic.
    _definition_fields = ['subjects', 'resources', 'actions']

    def __init__(self, uid, subjects=(), effect=DENY_ACCESS, resources=(),
                 actions=(), context=None, rules=None, description=None):
        self.uid = uid
        self.subjects = subjects
        self.effect = effect or DENY_ACCESS
        self.resources = resources
        self.actions = actions
        # check for deprecated rules argument.
        # If both 'context' and 'rules' are present - 'context' wins
        if context is not None:
            pass
        elif rules:
            warnings.warn("'rules' argument will be removed in next version. Use 'context' argument",
                          DeprecationWarning, stacklevel=2)
            context = rules
        else:
            context = {}
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
            context_rules = props['context']
        elif 'rules' in props:  # this is to support deprecated 'rules' attribute
            context_rules = props['rules']
            del props['rules']
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
        self._check_fields_type()
        # always calculate type. Even if type is set explicitly. Dict assign eliminates recursion
        self.__dict__['type'] = self._calculate_type()

    def _calculate_type(self):
        for elements in [getattr(self, f, ()) for f in self._definition_fields]:
            if any([isinstance(e, dict) for e in elements]):
                return TYPE_RULE_BASED
        return TYPE_STRING_BASED

    def _check_fields_type(self):
        """Checks type of a field that defines Policy"""
        for field_name in self._definition_fields:
            if hasattr(self, field_name):
                for e in getattr(self, field_name):
                    if not isinstance(e, (str, dict)):
                        raise PolicyCreationError(
                            'Field "%s" element must be of `str` or `dict` type. But given: %s' % (field_name, e)
                        )
        if hasattr(self, 'context') and not isinstance(self.context, dict):
            raise PolicyCreationError('Error creating Policy. Context must be a dictionary')

    def _data(self):
        data = vars(self)
        # get rid of "py/tuple" for tuples upon serialization in favor of simple json-array
        for k, prop in data.items():
            if isinstance(prop, tuple):
                data[k] = list(prop)
        return data
