import threading

from ..manager import PolicyManager


class MemoryManager(PolicyManager):
    """Stores all policies in memory"""

    def __init__(self):
        self.policies = {}
        self.lock = threading.Lock()

    def get(self, id):
        self.lock.acquire()
        try:
            return self.policies.get(id)
        finally:
            self.lock.release()

    def delete(self, id):
        self.lock.acquire()
        try:
            del self.policies[id]
        finally:
            self.lock.release()
