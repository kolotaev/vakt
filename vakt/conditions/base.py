import json
import importlib
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
    def from_json(cls, json_data):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ConditionCreationError('Invalid JSON data. JSON error: %s' % e)
        if 'contents' not in data:
            raise ConditionCreationError("No 'contents' key in JSON data found")
        if 'type' not in data:
            raise ConditionCreationError("No 'type' key in JSON data found")
        m = importlib.import_module(cls.__mro__[0].__module__)
        m = getattr(m, data['type'])
        return m._create_from_dictionary(data)

    def _data(self):
        return {
            'type': self.name(),
            'contents': self.__dict__,
        }

    @classmethod
    def _create_from_dictionary(cls, data):
        """Factory for creating various Condition from dictionary"""
        o = cls.__new__(cls)
        if 'contents' not in data:
            raise ConditionCreationError("No 'contents' key in JSON data found")
        given_args_len = len(data['contents'])
        expected_args_len = len(signature(cls.__init__).parameters)-1
        if given_args_len != expected_args_len:
            raise ConditionCreationError(
                'Number of arguments does not match. Given %d. Expected %d' % (given_args_len, expected_args_len))
        for k, v in data.items():
            setattr(o, k, v)
        return o
