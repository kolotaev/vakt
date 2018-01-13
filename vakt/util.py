import json


class JsonDumper:
    """Mixin for dumping object to JSON"""

    def __repr__(self):
        self.to_json()

    def to_json(self):
        """Get JSON representation of an object"""
        return json.dumps(self.__dict__, default=self._serializer)

    def _serializer(self, obj):
        """JSON serializer for objects not supported by default json encoder"""
        if isinstance(obj, self.__class__):
            return obj.to_json()
        return obj.__dict__
