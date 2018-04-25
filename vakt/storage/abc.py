"""
Contains interfaces that all Storages should implement.
"""

from abc import ABCMeta, abstractmethod


class Storage(metaclass=ABCMeta):
    """
    Interface for any storage that persists policies.
    Every storage should implement all the specified methods, but how, it's up to it to decide:
    it can be in-memory storage, SQL database, NoSQL solution, etc.
    """

    @abstractmethod
    def add(self, policy):
        """Store a policy"""
        pass

    @abstractmethod
    def get(self, uid):
        """Retrieve specific policy"""
        pass

    @abstractmethod
    def get_all(self, limit, offset):
        """Retrieve all the policies within a window"""
        pass

    @abstractmethod
    def find_for_inquiry(self, inquiry):
        """
        Get potential policies for a given inquiry.
        Storage is free to decide what policies to return based on the performance and implementation considerations.
        In the worst case - all policies. In the best - policies matched on actions, subjects, resources.
        Mediocre case - match on subject.
        """
        pass

    @abstractmethod
    def update(self, policy):
        """Update a policy"""
        pass

    @abstractmethod
    def delete(self, uid):
        """Delete a policy"""
        pass
