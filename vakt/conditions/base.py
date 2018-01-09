from abc import ABC, abstractmethod


class Condition(ABC):
    """Basic Condition"""

    def get_name(self):
        """Get condition name"""
        return self.__class__.__name__

    @abstractmethod
    def satisfied(self, what, request):
        """Is the condition satisfied by the request"""
        pass
