import json
from vakt.constants import *


class Policy:
    """Represents a policy that regulates access and allowed actions of subjects
    over some resources under a set of conditions."""

    def __init__(self, id, description=None, subjects=[], effect=None, resources=[], actions=[], conditions=[]):
        self._id = id
        self._description = description
        self._subjects = subjects
        self._effect = effect
        self._resources = resources
        self._actions = actions
        self._conditions = conditions

    @classmethod
    def from_json(cls, data):
        """Create Policy from json string"""
        try:
            props = json.loads(data)
        except json.JSONDecodeError as e:
            print("Error creating policy from json.", e)

        return Policy(props['id'], props['description'], props['subjects'],  props['effect'],
                      props['resources'], props['actions'], props['conditions'])

    @property
    def id(self):
        return self.id

    @property
    def description(self):
        return self._description

    @property
    def description(self):
        return self._description

    @property
    def subjects(self):
        return self._subjects

    @property
    def effect(self):
        return self._effect

    @property
    def resources(self):
        return self._resources

    @property
    def subjects(self):
        return self._subjects

    @property
    def actions(self):
        return self._actions

    @property
    def conditions(self):
        return self._conditions

    def allow_access(self):
        return self.effect == ALLOW_ACCESS

    @property
    def start_delimiter(self):
        return '<'

    @property
    def end_delimiter(self):
        return '>'
