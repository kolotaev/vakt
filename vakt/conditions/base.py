import json
from abc import ABC, abstractmethod
from inspect import signature

from ..util import JsonDumper
from ..exceptions import ConditionCreationError


class Condition(ABC, JsonDumper):
    """Basic Condition"""

    @abstractmethod
    def satisfied(self, what, request):
        """Is the condition satisfied by the request"""
        pass

    def name(self):
        """Get condition name"""
        return self.__class__.__name__

    @classmethod
    def from_json(cls, data):
        jc = json.loads(data)
        klass = globals()[jc['type']]
        return klass._create_from_dictionary(data)

    def _data(self):
        return {
            'type': self.name(),
            'contents': self.__dict__,
        }

    @classmethod
    def _create_from_dictionary(cls, data):
        """Factory for creating various Condition from dictionary"""
        o = cls.__new__(cls)
        given_args_len = len(data)
        expected_args_len = len(signature(cls.__init__).parameters)-1
        if given_args_len != expected_args_len:
            raise ConditionCreationError(
                'Number of arguments does not match. Given %d. Expected %d' % (given_args_len, expected_args_len))
        for k, v in data.items():
            setattr(o, k, v)
        return o
