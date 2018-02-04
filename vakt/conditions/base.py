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
        parts = data['type'].split('.')
        m = importlib.import_module(".".join(parts[:-1]))
        klass = getattr(m, parts[-1])

        o = klass.__new__(klass)
        given_args_len = len(data['contents'])
        expected_args_len = len(signature(klass.__init__).parameters)-1
        if given_args_len != expected_args_len:
            raise ConditionCreationError(
                'Number of arguments does not match. Given %d. Expected %d' % (given_args_len, expected_args_len))
        for k, v in data['contents'].items():
            setattr(o, k, v)
        return o

    def _data(self):
        return {
            'type': '%s.%s' % (self.__class__.__module__, self.__class__.__name__),
            'contents': self.__dict__,
        }
