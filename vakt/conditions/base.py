from abc import ABC, abstractmethod

from ..util import JsonDumper


class Condition(ABC, JsonDumper):
    """Basic Condition"""

    @abstractmethod
    def satisfied(self, what, request):
        """Is the condition satisfied by the request"""
        pass

    @classmethod
    def _create_from_dictionary(cls, dictionary):
        pass

    def name(self):
        """Get condition name"""
        return self.__class__.__name__

    def data(self):
        return super()

    @classmethod
    def from_json(cls, data):
        return Condition()
