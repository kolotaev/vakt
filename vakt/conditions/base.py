from abc import ABC, abstractmethod


class Condition(ABC):
    """Basic Condition"""

    def get_name(self):
        """Get condition name"""
        return self.__class__.__name__

    @abstractmethod
    def fulfills(self, what, request):
        """Is request fulfilled by the condition"""
        pass
