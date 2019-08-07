import yaml

from .abc import Reader
from ..policy import Policy
from ..effects import ALLOW_ACCESS, DENY_ACCESS
from ..exceptions import PolicyCreationError
from ..util import merge_dicts
from ..rules.base import Rule
from ..exceptions import PolicyReadError


class YamlReader(Reader):
    """
    Reads policies from YAML file with policies definitions.

    """
    def __init__(self, file, custom_rules_map=None):
        self.file = file
        self.auto_increment_counter = 1
        self.rules_map = self.get_rules_map(custom_rules_map)

    def read(self):
        """
        Reads policies definitions from YAML file.
        If some policy fails to be created from definition PolicyReadError is raised.
        """
        f = open(self.file, 'r')
        try:
            for data in yaml.safe_load_all(f):
                try:
                    yield self._policy_from_definition(data)
                except Exception as e:
                    raise PolicyReadError(e, data)
        finally:
            f.close()

    def populate(self, storage):
        for policy in self.read():
            storage.add(policy)

    def _policy_from_definition(self, data):
        """
        Create policy from YAML definition
        """
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
        policy_data['actions'] = self._convert_attributes_list(data.get('actions', []))
        policy_data['resources'] = self._convert_attributes_list(data.get('resources', []))
        policy_data['subjects'] = self._convert_attributes_list(data.get('subjects', []))
        context = self._convert_attributes_list(data.get('context', []))
        if len(context) > 0:
            # context can have only one dict-based definition. Others will be discarded
            policy_data['context'] = context[0]
        return Policy(**policy_data)

    def _convert_attributes_list(self, elements):
        result = []
        if not isinstance(elements, list):
            raise TypeError('elements in yaml file must be a list')
        for el in elements:
            if isinstance(el, str):
                result.append(el)
            elif isinstance(el, dict):
                result.append(self._process_rule_based_definition(el))
        return result

    def _process_rule_based_definition(self, definition):
        result = {}
        for k, v in definition.items():
            if k in self.rules_map:  # if it's a Rule-name, e.g. {In: [12, 13]}
                klass, args, kwargs = self.rules_map[k], [], {}
                if v is None:  # for 0-args Rules: e.g. Any:
                    args = []
                elif not isinstance(v, (list, tuple)):  # for 1-arg Rules that are written in one line (Eq: 'Max')
                    args = [v]
                else:  # we have a list of simple or complex args for a Rule
                    for i in v:
                        if isinstance(i, dict):
                            i_val = self._process_rule_based_definition(i)
                            if isinstance(i_val, Rule):  # means we process compound Rule: And(Greater(1), Less(90))
                                args.append(i_val)
                            else:  # means it's a keyword argument of a non-compound Rule
                                kwargs = merge_dicts(kwargs, i_val)
                        else:
                            args.append(i)
                return klass(*args, **kwargs)
            else:  # it's a simple attribute name. e.g. {'city': someRule}
                if isinstance(v, (list, tuple)):
                    # only one rule is allowed for attribute! e.g.: {'nickname': Eq('Max)}
                    result[k] = self._process_rule_based_definition(v[0])
                else:
                    result[k] = v
        return result
