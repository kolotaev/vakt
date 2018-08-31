"""
Memory storage for Policies.
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
                raise PolicyExistsError(uid)
            self.policies[uid] = policy

    def get(self, uid):
        return self.policies.get(uid)

    def get_all(self, limit, offset):
        self._check_limit_and_offset(limit, offset)
        result = [v for v in self.policies.values()]
        if offset > len(result):
            return []
        if limit == 0:
            limit = len(result)
        return result[offset:limit+offset]

    def find_for_inquiry(self, inquiry, checker=None):
        with self.lock:
            return list(self.policies.values())

    def update(self, policy):
        self.policies[policy.uid] = policy

    def delete(self, uid):
        if uid in self.policies:
            del self.policies[uid]
