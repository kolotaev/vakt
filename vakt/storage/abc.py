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

        Returns Iterable
        """
        pass

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


class Migration(metaclass=ABCMeta):
    """
    Manager for maintaining various migration actions of the storage: schema, indices, etc
    """

    @property
    @abstractmethod
    def order(self):
        """ Number of this migration in the row of migrations """
        pass

    @abstractmethod
    def up(self):
        """ Migrate DB schema up """
        pass

    @abstractmethod
    def down(self):
        """ Migrate DB schema down """
        pass
