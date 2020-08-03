"""
Contains interfaces that all Readers should implement.
"""

from abc import ABCMeta, abstractmethod
import threading

import vakt.rules as rules
from vakt.util import merge_dicts


# Define out-of-the box Rules mapping (name -> class)
RULES_MAP = {}
for k, v in vars(rules).items():
    if type(v) == ABCMeta and vars(v)['__module__'].startswith('vakt.rules'):
        RULES_MAP[k] = v


class Reader(metaclass=ABCMeta):

    def __init__(self):
        self._lock = threading.Lock()
        self._counter = 0

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

    @property
    def counter(self):
        """
        Auto-incrementing counter
        """
        with self._lock:
            self._counter += 1
            return self._counter
