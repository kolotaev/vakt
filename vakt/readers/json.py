import json

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
        f = open(self.file, 'r')
        try:
            for data in json.loads(f):
                try:
                    yield Policy(self.auto_increment_counter)
                except Exception as e:
                    raise PolicyReadError(e, data)
        finally:
            f.close()

    def populate(self, storage):
        pass
