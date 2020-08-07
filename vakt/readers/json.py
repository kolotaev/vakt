import json

from .abc import Reader
from ..policy import Policy
from ..exceptions import PolicyReadError


class JSONReader(Reader):
    """
    Reads policies from JSON file with policies definitions.

    """
    def __init__(self, file, custom_rules_map=None):
        super().__init__()
        self.file = file
        self.rules_map = self.get_rules_map(custom_rules_map)
        self._check_file()

    def read(self):
        """
        Reads policies definitions from JSON file.
        If some policy fails to be created from definition PolicyReadError is raised.
        """
        with open(self.file) as f:
            data = f.read()
            try:
                for data in json.loads(data):
                    yield Policy(self.counter)
            except Exception as e:
                raise PolicyReadError(e, self, data)
