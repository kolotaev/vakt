import json
from abc import abstractmethod


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

    def to_json(self):
        """
        Get JSON representation of an object
        """
        return json.dumps(self._data(),
                          sort_keys=True,
                          default=lambda o: o.to_json() if isinstance(o, JsonDumper) else vars(o))

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
