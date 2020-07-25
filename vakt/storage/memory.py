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
            log.info('Added Policy: %s', policy)

    def get(self, uid):
        return self.policies.get(uid)

    def get_all(self, limit, offset):
        self._check_limit_and_offset(limit, offset)
        result = [v for v in self.policies.values()]
        if offset > len(result) or limit == 0:
            return []
        return result[offset:limit+offset]

    def find_for_inquiry(self, inquiry, checker=None):
        with self.lock:
            return self.policies.values()

    def update(self, policy):
        with self.lock:
            if policy.uid not in self.policies:
                return
            self.policies[policy.uid] = policy
        log.info('Updated Policy with UID=%s. New value is: %s', policy.uid, policy)

    def delete(self, uid):
        if uid in self.policies:
            del self.policies[uid]
            log.info('Policy with UID %s was deleted', uid)
