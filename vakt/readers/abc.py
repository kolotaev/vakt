"""
Contains interfaces that all Readers should implement.
"""

from abc import ABCMeta, abstractmethod

import vakt.rules as rules
from vakt.util import merge_dicts


# Define out-of-the box Rules mapping (name -> class)
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
        return merge_dicts(RULES_MAP, custom_rules_map)

