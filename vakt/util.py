"""
Utility functions and classes for Vakt.
"""

import logging
from abc import ABCMeta, abstractmethod

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
        return "%s <Object ID %s>: %s" % (self.__class__, id(self), vars(self))


class Subject:
    """
    Publisher of events in the pub-sub objects relation
    """
    def __init__(self):
        self._listeners = []

    def add_listener(self, listener):
        """
        Attach listener to this subject
        """
        self._listeners.append(listener)

    def remove_listener(self, listener):
        """
        Detach listener from this subject
        """
        self._listeners.remove(listener)

    def notify(self):
        """
        Notify all attached listeners about event
        """
        for listener in self._listeners:
            listener.update()


class Observer(metaclass=ABCMeta):
    """
    Observer of the events in the pub-sub objects relation
    """
    @abstractmethod
    def update(self):
        """
        Update observer on notify event
        """
        pass
