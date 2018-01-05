import json


class JsonDumper:
    """Trait for dumping object to JSON"""

    def to_json(self):
        """Get JSON representation of an object"""
        return json.dumps(self.__dict__)
