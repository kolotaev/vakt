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
        policy_data = {}
        if 'uid' in data:
            policy_data['uid'] = data['uid']
        else:
            policy_data['uid'] = self.auto_increment_counter
            self.auto_increment_counter += 1
        if 'description' in data:
            policy_data['description'] = data['description'].strip()
        effect = data['effect'].strip()
        if effect not in (ALLOW_ACCESS, DENY_ACCESS):
            raise PolicyCreationError('Unknown policy effect: "%s"', effect)
        policy_data['effect'] = effect
        policy_data['actions'] = self._convert_attributes_list(data['actions'])
        policy_data['resources'] = self._convert_attributes_list(data['resources'])
        policy_data['subjects'] = self._convert_attributes_list(data['subjects'])
        return Policy(**policy_data)

    @staticmethod
    def _convert_attributes_list(elements):
        result = []
        if not elements:
            return None
        if not isinstance(elements, list):
            raise TypeError('elements in yaml file must be a list')
        for el in elements:
            if isinstance(el, str):
                result.append(el)
        return result
