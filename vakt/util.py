"""
Utility functions and classes for Vakt.
"""

import json
import logging
from abc import abstractmethod


log = logging.getLogger(__name__)


class JsonDumper:
    """
    Mixin for dumping object to JSON
    """

    @classmethod
    @abstractmethod
    def from_json(cls, data):
        """
        Create object from a JSON string
        Returns a new instance of a class
        """
        pass

    def to_json(self, sort=False):
        """
        Get JSON representation of an object
        """
        return json.dumps(self._data(),
                          sort_keys=sort,
                          default=lambda o: o.to_json() if isinstance(o, JsonDumper) else vars(o))

    @classmethod
    def _parse(cls, data):
        """Parse JSON string and return data"""
        try:
            return json.loads(data)
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
        return "%s: %s" % (self.__class__, vars(self))
