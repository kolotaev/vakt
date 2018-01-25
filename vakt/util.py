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
        def serializer(obj):
            if isinstance(obj, JsonDumper):
                return obj.to_json()
            return obj.__dict__
        return json.dumps(self._data(), default=serializer)

    def _data(self):
        """
        Get the object data. Is useful for overriding in custom classes
        """
        return self.__dict__
