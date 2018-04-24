"""
Memory storage.
"""

import threading
import logging

from ..storage.abc import Storage
from ..exceptions import PolicyExistsError


log = logging.getLogger(__name__)


class MemoryStorage(Storage):
    """Stores all policies in memory"""

    def __init__(self):
        self.policies = {}
        self.lock = threading.Lock()

    def add(self, policy):
        uid = policy.uid
        with self.lock:
            if uid in self.policies:
                log.error('Error trying to create already existing policy with UID=%s', uid)
                raise PolicyExistsError
            self.policies[uid] = policy

    def get(self, uid):
        return self.policies.get(uid)

    def get_all(self, limit, offset):
        result = [v for v in self.policies.values()]
        if limit + offset > len(result):
            limit = len(result)
            offset = 0
        return result[offset:limit + offset]

    def find_for_inquiry(self, inquiry):
        with self.lock:
            return list(self.policies.values())

    def update(self, policy):
        self.policies[policy.uid] = policy

    def delete(self, uid):
        if uid in self.policies:
            del self.policies[uid]
