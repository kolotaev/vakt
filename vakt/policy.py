import json

from .effects import *
from .exceptions import PolicyCreationError
from .util import JsonDumper
from .conditions.base import Condition


class DefaultPolicy(JsonDumper):
    """Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of conditions."""

    def __init__(self, id, description=None, subjects=(), effect=DENY_ACCESS, resources=(), actions=(), conditions=()):
        self.id = id
        self.description = description
        self.subjects = subjects
        self.effect = effect
        self.resources = resources
        self.actions = actions
        self.conditions = conditions

    @classmethod
    def from_json(cls, data):
        try:
            props = json.loads(data)
        except json.JSONDecodeError as e:
            # todo - logging
            # print("Error creating policy from json.", e)
            raise e
        if 'id' not in props:
            raise PolicyCreationError("Error creating policy from json. 'id' attribute is required")

        conditions = []
        if 'conditions' in props:
            for c in props['conditions']:
                conditions.append(Condition.from_json(c))

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
