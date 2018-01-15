import json
from abc import abstractmethod


class JsonDumper:
    """Mixin for dumping object to JSON"""

    @classmethod
    @abstractmethod
    def from_json(cls, data):
        """Create object from a JSON string
           Returns a new instance of a class"""
        pass

    def to_json(self):
        """Get JSON representation of an object"""
        return json.dumps(self.data(), default=self._serializer)

    def data(self):
        """Get the object data. Is useful for overriding in custom classes"""
        return self.__dict__

    def _serializer(self, obj):
        """JSON serializer for objects not supported by default json encoder"""
        if isinstance(obj, self.__class__):
            return obj.to_json()
        return obj.__dict__
