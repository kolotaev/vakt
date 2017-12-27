from abc import ABC, abstractmethod


class Request(ABC):
    """
    Request object that holds all the information about the requested resource intent.
    Is responsible to decisions is the requested intent allowed or not.
    """

    def __init__(self, resource, action, subject, context=None):
        self.resource = resource
        self.action = action
        self.subject = subject
        self.context = context

    @abstractmethod
    def is_allowed(self):
        """Is requested intent allowed or not?"""
        pass
