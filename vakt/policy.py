"""
Namespace for a basic Policy class.
"""

import logging
import warnings
import copy

from .effects import ALLOW_ACCESS, DENY_ACCESS
from .exceptions import PolicyCreationError
from .util import JsonSerializer, PrettyPrint
from .rules.base import Rule


log = logging.getLogger(__name__)


# Types for Policies and Inquiries:
# String-based (simple strings, regexps)
TYPE_STRING_BASED = 1
# Rule-based definitions (Rules).
TYPE_RULE_BASED = 2


class Policy(JsonSerializer, PrettyPrint):
    """Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of context restrictions.
    """

    # Fields that affect Policy definition and further logic for `fit`.
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
            warnings.warn("'rules' argument will be removed in version 2.0. Use 'context' argument",
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
        """
        Policy expression start tag.
        Used for policies defined with regexp.
        """
        return '<'

    @property
    def end_tag(self):
        """
        Policy expression end tag.
        Used for policies defined with regexp.
        """
        return '>'

    def __setattr__(self, name, value):
        self._check_field_type(name, value)
        # Always calculate type. Even if type is set explicitly.
        calculated_type = self._calculate_type(name, value)
        object.__setattr__(self, name, value)
        # Dict assign eliminates recursion
        self.__dict__['type'] = calculated_type

    def _calculate_type(self, new_element_name, new_element_value):
        all_elements = rule_elements = str_elements = 0
        self_copy = copy.copy(self)
        self_copy.__dict__[new_element_name] = new_element_value
        for elements in [getattr(self_copy, f, ()) for f in self._definition_fields]:
            for e in elements:
                all_elements += 1
                if isinstance(e, (dict, Rule)):
                    rule_elements += 1
                elif isinstance(e, str):
                    str_elements += 1
        if all_elements == str_elements or all_elements == 0:
            return TYPE_STRING_BASED
        if all_elements == rule_elements:
            return TYPE_RULE_BASED
        raise PolicyCreationError(
            'Policy elements should all be either dict, Rule (for rule-based) or string (for string-based)'
        )

    def _check_field_type(self, name, value):
        """Checks type of a field that defines Policy"""
        if name in self._definition_fields and not all(map(lambda x: isinstance(x, (str, dict, Rule)), value)):
            raise PolicyCreationError(
                'Field "%s" element must be of `str`, `dict` or `Rule` type. But given: %s' % (name, value)
            )
        if name == 'context' and not isinstance(value, dict):
            raise PolicyCreationError('Error creating Policy. Context must be a dictionary')

    def _data(self):
        data = vars(self)
        # get rid of "py/tuple" for tuples upon serialization in favor of simple json-array
        for k, prop in data.items():
            if isinstance(prop, tuple):
                data[k] = list(prop)
        return data


class PolicyAllow(Policy):
    """
    Policy that has effect ALLOW_ACCESS by default.
    """
    def __init__(self, uid, subjects=(), resources=(), actions=(), context=None, description=None):
        super().__init__(uid, effect=ALLOW_ACCESS,
                         subjects=subjects, resources=resources,
                         actions=actions, context=context, description=description)


class PolicyDeny(Policy):
    """
    Policy that has effect DENY_ACCESS by default.
    """
    def __init__(self, uid, subjects=(), resources=(), actions=(), context=None, description=None):
        super().__init__(uid, effect=DENY_ACCESS,
                         subjects=subjects, resources=resources,
                         actions=actions, context=context, description=description)
