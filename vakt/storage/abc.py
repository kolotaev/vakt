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
        """
        Retrieve all the policies within a window.

        All storages must have the same behaviour when using limit=0: return empty list.

        Returns Iterable
        """
        pass

    def retrieve_all(self, batch=50):
        """
        Retrieve all the policies from the storage in batches of a specified size.
        Stops when all the existing policies from a storage where returned.
        You can specify a size of a batch of policies for each iteration.

        Returns generator
        """
        limit, offset = batch, 0
        while True:
            policies = list(self.get_all(limit, offset))
            if len(policies) == 0:
                return
            for policy in policies:
                yield policy
            offset = offset + limit

    @abstractmethod
    def find_for_inquiry(self, inquiry, checker=None):
        """
        Get potential policies for a given inquiry.
        Storage is free to decide what policies to return based on the performance and implementation considerations.
        In the worst case - all policies. In the best - policies matched on actions, subjects, resources.
        Mediocre case - match on subject.

        Checker is argument based on the class of provided vakt.checker.*
        This internal checker is responsible for generating the correct type of query to the Storage:
        e.g. RegexChecker, StringExactChecker will result in different queries.

        Returns Iterable
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

    @staticmethod
    def _check_limit_and_offset(limit, offset):
        if limit < 0:
            raise ValueError("Limit can't be negative")
        if offset < 0:
            raise ValueError("Offset can't be negative")
