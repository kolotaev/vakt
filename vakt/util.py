"""
Utility functions and classes for Vakt.
"""

import logging

import jsonpickle


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
    def _parse(cls, data):
        """Parse JSON string and return data"""
        try:
            return jsonpickle.decode(data)
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
