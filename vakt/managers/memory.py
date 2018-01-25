import threading

from ..manager import PolicyManager


class MemoryManager(PolicyManager):
    """Stores all policies in memory"""

    def __init__(self):
        self.policies = {}
        self.lock = threading.Lock()

    def get(self, id):
        with self.lock:
            return self.policies.get(id)

    def delete(self, id):
        with self.lock:
            del self.policies[id]
