import json
import threading

from .abc import Reader
from ..policy import Policy
from ..exceptions import PolicyReadError


class JSONReader(Reader):
    """
    Reads policies from JSON file with policies definitions.

    """
    def __init__(self, file, custom_rules_map=None):
        self.file = file
        self.auto_increment_counter = 1
        self.rules_map = self.get_rules_map(custom_rules_map)

    def read(self):
        """
        Reads policies definitions from JSON file.
        If some policy fails to be created from definition PolicyReadError is raised.
        """
        with open(self.file) as f:
            data = f.read()
            for data in json.loads(data):
                try:
                    yield Policy(self._inc())
                except Exception as e:
                    raise PolicyReadError(e, data)

    def populate(self, storage):
        pass
