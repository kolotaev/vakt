"""
Contains interfaces that all Readers should implement.
"""

from abc import ABCMeta, abstractmethod

import vakt.rules as rules


RULES_MAP = {}
for k, v in vars(rules).items():
    if type(v) == ABCMeta and vars(v)['__module__'].startswith('vakt.rules'):

        RULES_MAP[k] = v


class Reader(metaclass=ABCMeta):
    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def populate(self, storage):
        pass

    @staticmethod
    def get_rules_map(custom_rules_map=None):
        if custom_rules_map is None:
            custom_rules_map = {}
        rules_map = RULES_MAP.copy()
        rules_map.update(custom_rules_map)
        return rules_map
