import yaml

from .abc import Reader
from ..policy import Policy
from ..effects import ALLOW_ACCESS, DENY_ACCESS
from ..exceptions import PolicyCreationError


class YamlReader(Reader):
    """
    Reads policies from YAML file with policies definitions
    """
    def __init__(self, file):
        self.file = file
        self.auto_increment_counter = 1

    def read(self):
        f = open(self.file, 'r')
        try:
            for data in yaml.safe_load_all(f):
                yield self._policy_from_definition(data)
        finally:
            f.close()

    def populate(self, storage):
        for policy in self.read():
            storage.add(policy)

    def _policy_from_definition(self, data):
        if 'uid' in data:
            uid = data['uid']
        else:
            uid = self.auto_increment_counter
            self.auto_increment_counter += 1
        if 'description' in data:
            description = data['description'].strip()
        effect = data['effect'].strip()
        if effect not in (ALLOW_ACCESS, DENY_ACCESS):
            raise PolicyCreationError('Unknown policy effect: "%s"', effect)
        return Policy(uid=uid, description=description, effect=effect)
