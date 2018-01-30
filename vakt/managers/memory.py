import threading

from ..manager import PolicyManager
from ..exceptions import PolicyExists


class MemoryManager(PolicyManager):
    """Stores all policies in memory"""

    def __init__(self):
        self.policies = {}
        self.lock = threading.Lock()

    def create(self, policy):
        id = policy.id
        with self.lock:
            if id in self.policies:
                raise PolicyExists
            self.policies[id] = policy

    def get(self, id):
        return self.policies.get(id)

    def get_all(self, limit, offset):
        result = [v for k, v in self.policies.items()]
        if limit + offset > len(result):
            limit = len(result)
            offset = 0
        return result[offset:limit + offset]

    def find_by_request(self, request):
        with self.lock:
            return [p for i, p in self.policies.items() if request.subject in p.subjects]

    def update(self, policy):
        self.policies[policy.id] = policy

    def delete(self, id):
        if id in self.policies:
            del self.policies[id]
