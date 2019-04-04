"""
Base Rule. Should be extended be concrete ones.
"""

import logging
from abc import ABCMeta, abstractmethod

from ..util import JsonSerializer, PrettyPrint
from ..exceptions import RuleCreationError


log = logging.getLogger(__name__)


class Rule(JsonSerializer, PrettyPrint, metaclass=ABCMeta):
    """Basic Rule"""

    @abstractmethod
    def satisfied(self, what, inquiry=None):
        """Is rule satisfied by the inquiry"""
        pass

    @classmethod
    def from_json(cls, data):
        try:
            return cls._parse(data)
        except ValueError as e:
            raise RuleCreationError(str(e))

    def _data(self):
        return self
