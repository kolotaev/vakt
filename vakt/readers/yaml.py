import yaml

from .abc import Reader
from ..policy import Policy
from ..effects import ALLOW_ACCESS, DENY_ACCESS
from ..exceptions import PolicyCreationError


class YamlReader(Reader):
    """
    Reads policies from YAML file with policies definitions
    """
    def __init__(self, file, custom_rules_map=None):
        self.file = file
        self.auto_increment_counter = 1
        self.rules_map = self.get_rules_map(custom_rules_map)

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
        effect = data.get('effect', '')
        if effect not in (ALLOW_ACCESS, DENY_ACCESS):
            raise PolicyCreationError('Unknown policy effect: "%s"' % effect)
        policy_data['effect'] = effect
        policy_data['actions'] = self.convert_attributes_list(data.get('actions', []))
        policy_data['resources'] = self.convert_attributes_list(data.get('resources', []))
        policy_data['subjects'] = self.convert_attributes_list(data.get('subjects', []))
        return Policy(**policy_data)

    def convert_attributes_list(self, elements):
        result = []
        if not isinstance(elements, list):
            raise TypeError('elements in yaml file must be a list')
        for el in elements:
            if isinstance(el, str):
                result.append(el)
            elif isinstance(el, dict):
                # result.append([])
                result.append(self.process_rule_based_definition(el))
        return result

    def process_rule_based_definition(self, definition):
        result = {}
        for k, v in definition.items():
            if k in self.rules_map:
                klass = self.rules_map[k]
                args = []
                kwargs = {}
                if v is None:
                    args = []
                elif not isinstance(v, (list, tuple)):
                    args = [v]
                else:
                    for i in v:
                        if isinstance(i, dict):
                            kwargs = self._merge_dicts(kwargs, i)
                        else:
                            args.append(i)
                return klass(*args, **kwargs)
            else:
                if not result:
                    result = {}
                result[k] = self.process_rule_based_definition(v[0])
        return result

    def _merge_dicts(self, x, y):
        z = x.copy()
        z.update(y)
        return z
