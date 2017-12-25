import json


class Policy():
    """
    Represents a policy that regulates access and allowed actions of subjects over some resources under a set of conditions.
    """

    def __init__(self, id, description=None, subjects=[], effect=None, resources=[], actions=[], conditions=[]):
        self.id = id
        self.description = description
        self.subjects = subjects
        self.effect = effect
        self.resources = resources
        self.actions = actions
        self.conditions = conditions


    @classmethod
    def fromJson(data):
        """Create Policy from json string"""
        try:
            props = json.loads(data)
        except Error as e:
            print("Error creating policy from json.", e)

        self.id = props['id']
        self.description = props['description']
        self.subjects = props['subjects']
        self.effect = props['effect']
        self.resources = props['resources']
        self.actions = props['actions']
        self.conditions = props['conditions']


    @property
    def id(self):
        self._id


    @property
    def description(self):
        self._description


    @property
    def description(self):
        self._description


    @property
    def subjects(self):
        self._subjects


    @property
    def effect(self):
        self._effect


    @property
    def resources(self):
        self._resources


    @property
    def subjects(self):
        self._subjects


    @property
    def actions(self):
        self._actions


    @property
    def conditions(self):
        self._conditions


    def allow_access(self):
        return self.effect == ALLOW_ACCESS


    def start_delimeter(self):
        return '<'


    def end_delimeter(self):
        return '>'
