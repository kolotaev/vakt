"""
Cahing mechanisms for vakt
"""

from .exceptions import (
    PolicyExistsError, PolicyUpdateError,
    PolicyCreationError, PolicyDeletionError
)

class Wrap:
    """
    Wraps all underlying storage interface calls with a cache that is represented by another storage.
    Typical usage might be:
    storage = Wrap(MongoStorage(...), cache=MemoryStorage(), init=True)
    """

    def __init__(self, storage, cache, init=False):
        self.storage = storage
        self.cache = cache
        if init:
            offset = 0
            while True:
                policies = self.storage.get_all(10000, offset)
                if not policies:
                    break
                for p in policies:
                    self.cache.add(p)
                offset += 1

    def add(self, policy):
        """
        Cache storage `add`
        """
        try:
            self.storage.add(policy)
        except PolicyExistsError:
            pass
        self.cache.add(policy)

    def get(self, uid):
        """
        Cache storage `get`
        """
        policy = self.cache.get(uid)
        if policy:
            return policy
        return self.storage.get(uid)

    def get_all(self, limit, offset):
        """
        Cache storage `get_all`
        """
        result = self.cache.get_all(limit, offset)
        if result:
            return result
        return self.storage.get_all(limit, offset)

    def find_for_inquiry(self, inquiry, checker=None):
        """
        Cache storage `find_for_inquiry`
        """
        result = self.cache.find_for_inquiry(inquiry, checker)
        if result:
            return result
        return self.storage.find_for_inquiry(inquiry, checker)

    def update(self, policy):
        """
        Cache storage `update`
        """
        try:
            self.storage.update(policy)
        except (PolicyUpdateError, PolicyCreationError):
            pass
        self.cache.update(policy)

    def delete(self, uid):
        """
        Cache storage `delete`
        """
        try:
            self.storage.delete(uid)
        except PolicyDeletionError:
            pass
        self.cache.delete(uid)
