"""
Base Rule. Should be extended be concrete ones.
"""

import json
import logging
import importlib
from abc import ABCMeta, abstractmethod
from inspect import signature

from ..util import JsonDumper, PrettyPrint
from ..exceptions import RuleCreationError


log = logging.getLogger(__name__)


class Rule(JsonDumper, PrettyPrint, metaclass=ABCMeta):
    """Basic Rule"""

    @abstractmethod
    def satisfied(self, what, inquiry):
        """Is rule satisfied by the inquiry"""
        pass

    @classmethod
    def from_json(cls, data):
        try:
            data = json.loads(data)
        except ValueError as e:
            log.exception('Error creating %s', cls.__name__)
            raise RuleCreationError('Invalid JSON data. JSON error: %s' % e)
        if 'contents' not in data:
            log.exception('Error creating %s. No "contents" key in JSON data found', cls.__name__)
            raise RuleCreationError("No 'contents' key in JSON data found")
        if 'type' not in data:
            log.exception('Error creating %s. No "type" key in JSON data found', cls.__name__)
            raise RuleCreationError("No 'type' key in JSON data found")
        parts = data['type'].split('.')
        module = importlib.import_module(".".join(parts[:-1]))
        klass = getattr(module, parts[-1])

        obj = klass.__new__(klass)
        given_args_len = len(data['contents'])
        expected_args_len = len(signature(klass.__init__).parameters)-1
        if given_args_len != expected_args_len:
            log.exception('Error creating %s. Mismatched number of arguments', cls.__name__)
            raise RuleCreationError(
                'Number of arguments does not match. Given %d. Expected %d' % (given_args_len, expected_args_len))
        for k, v in data['contents'].items():
            setattr(obj, k, v)
        return obj

    def _data(self):
        return {
            'type': '%s.%s' % (self.__class__.__module__, self.__class__.__name__),
            'contents': self.__dict__,
        }
