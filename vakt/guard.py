from abc import ABC, abstractmethod


class Guard(ABC):
    """"""

    def __init__(self, resource, action, subject, context=None):
        self.resource = resource
        self.action = action
        self.subject = subject
        self.context = context

    @abstractmethod
    def is_allowed(self, request):
        """Is given request allowed or not?"""
        pass
