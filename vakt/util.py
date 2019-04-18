"""
Utility functions and classes for Vakt.
"""

import logging
import json

import jsonpickle

# from .policy import Policy
# from .guard import Inquiry
# from .exceptions import PolicyCreationError


log = logging.getLogger(__name__)


class JsonSerializer:
    """
    Mixin for dumping object to JSON
    """

    @classmethod
    def from_json(cls, data):
        """
        Create object from a JSON string
        Returns a new instance of a class
        """
        return cls._parse(data)

    def to_json(self, sort=False):
        """
        Get JSON representation of an object
        """
        jsonpickle.set_encoder_options('json', sort_keys=sort)
        return jsonpickle.encode(self._data())

    @classmethod
    def _parse(cls, string):
        """Parse JSON string and return data"""
        try:
            return jsonpickle.decode(string)
        except ValueError as err:
            log.exception('Error creating %s from json.', cls.__name__)
            raise err

    def _data(self):
        """
        Get the object data. Is useful for overriding in custom classes
        """
        return vars(self)


class PrettyPrint:
    """
    Allows to log objects with all the fields
    """
    def __str__(self):
        return "%s <Object ID %s>: %s" % (self.__class__, id(self), vars(self))


class JSONDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @staticmethod
    def dict_to_object(dic):
        """
        Implementation of serialization method of json.JSONDecoder
        """
        from .policy import Policy
        from .guard import Inquiry
        from .rules.base import Rule
        from .exceptions import PolicyCreationError, RuleCreationError
        js = json.dumps(dic)
        try:
            return Policy.from_json(js)
        except PolicyCreationError as e:
            if set(dic.keys()) - {'action', 'subject', 'context', 'resource'} == {}:
                return Inquiry.from_json(js)
        return dic


class JSONEncoder(json.JSONEncoder, json.JSONDecoder):
    def default(self, o):
        """
        Implementation of serialization method of json.JSONEncoder
        """
        if isinstance(o, JsonSerializer):
            return json.loads(o.to_json())
        return super().default(o)


# from vakt.rules import Eq, Greater, StrEqual
# from vakt.util import JSON
# import vakt
# import json
#
# i = vakt.Inquiry(action='get', resource='repos/john/tensorflow', subject='Max')
# p = vakt.Policy(1, actions=[Eq('foo'), Greater(9000), StrEqual('Je')], subjects=[{'name': Eq('Max')}])
#
# data = {'d': [45, 89, 7], 'i': i, 'p': p}
# print(json.dumps(data, cls=JSON))
