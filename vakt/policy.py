import json
import logging

from .effects import *
from .exceptions import PolicyCreationError
from .util import JsonDumper, PrettyPrint
from .conditions.base import Condition


log = logging.getLogger(__name__)


class DefaultPolicy(JsonDumper, PrettyPrint):
    """Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of conditions."""

    def __init__(self, id, description=None, subjects=(), effect=DENY_ACCESS, resources=(), actions=(), conditions=None):
        self.id = id
        self.description = description
        self.subjects = subjects
        self.effect = effect
        self.resources = resources
        self.actions = actions
        conditions = conditions or {}
        if not isinstance(conditions, dict):
            log.exception('Error creating Policy. Conditions must be a dictionary')
            raise PolicyCreationError("Error creating Policy. Conditions must be a dictionary")
        self.conditions = conditions

    @classmethod
    def from_json(cls, data):
        try:
            props = json.loads(data)
        except ValueError as e:
            log.exception("Error creating policy from json.", exc_info=True)
            raise e
        if 'id' not in props:
            log.exception("Error creating policy from json. 'id' attribute is required")
            raise PolicyCreationError("Error creating policy from json. 'id' attribute is required")

        conditions = {}
        if 'conditions' in props:
            for k, c in props['conditions'].items():
                conditions[k] = Condition.from_json(c)

        return cls(props['id'],
                   props.get('description'),
                   props.get('subjects', ()),
                   props.get('effect', DENY_ACCESS),
                   props.get('resources', ()),
                   props.get('actions', ()),
                   conditions)

    def allow_access(self):
        """Does policy imply allow-access?"""
        return self.effect == ALLOW_ACCESS

    @property
    def start_delimiter(self):
        """Policy expression start tag"""
        return '<'

    @property
    def end_delimiter(self):
        """Policy expression end tag"""
        return '>'
