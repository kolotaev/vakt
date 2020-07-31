"""
File storage for Policies.
"""

import logging

from ..storage.abc import Storage
from ..storage.memory import MemoryStorage


log = logging.getLogger(__name__)


class FileStorage(Storage):
    """
    Reads all policies from file and keeps them in the backing Storage (in memory by default).
    """

    def __init__(self, file, storage=None):
        if storage is None:
            self.back_store = MemoryStorage()

    def add(self, policy):
        # todo - raise exception for write-part
        return self.back_store.add(policy)

    def get(self, uid):
        return self.back_store.get(uid)

    def get_all(self, limit, offset):
        return self.back_store.get_all(limit, offset)

    def find_for_inquiry(self, inquiry, checker=None):
        return self.back_store.find_for_inquiry(inquiry, checker)

    def update(self, policy):
        return self.back_store.update(policy)

    def delete(self, uid):
        return self.back_store.update(uid)
