from abc import ABC, abstractmethod


class PolicyManager(ABC):
    """Interface for managers that persist policies.
    Every manager should implement all the specified methods, but how, it's up to it to decide:
    it can be in-memory storage, SQL database, NoSQL solution, etc."""

    @abstractmethod
    def get(self, id):
        """Retrieve specific policy"""
        pass

    @abstractmethod
    def get_all(self, limit, offset):
        """Retrieve all the policies within a window"""
        pass

    @abstractmethod
    def create(self, policy):
        """Create a policy"""
        pass

    @abstractmethod
    def update(self, policy):
        """Update a policy"""
        pass

    @abstractmethod
    def delete(self, id):
        """Delete a policy"""
        pass

    # todo - add method
