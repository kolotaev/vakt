import threading
import logging

from ..manager import PolicyManager
from ..exceptions import PolicyExists


log = logging.getLogger(__name__)


class MemoryManager(PolicyManager):
    """Stores all policies in memory"""

    def __init__(self):
        self.policies = {}
        self.lock = threading.Lock()

    def create(self, policy):
        id = policy.id
        with self.lock:
            if id in self.policies:
                log.error('Error trying to create already existing policy with ID=%s', id)
                raise PolicyExists
            self.policies[id] = policy

    def get(self, id):
        return self.policies.get(id)

    def get_all(self, limit, offset):
        result = [v for v in self.policies.values()]
        if limit + offset > len(result):
            limit = len(result)
            offset = 0
        return result[offset:limit + offset]

    def find_by_inquiry(self, inquiry):
        with self.lock:
            return list(self.policies.values())

    def update(self, policy):
        self.policies[policy.id] = policy

    def delete(self, id):
        if id in self.policies:
            del self.policies[id]
