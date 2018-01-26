import threading

from ..manager import PolicyManager
from ..exceptions import PolicyExists


class MemoryManager(PolicyManager):
    """Stores all policies in memory"""

    def __init__(self):
        self.policies = {}
        self.lock = threading.Lock()

    def get(self, id):
        return self.policies.get(id)

    def get_all(self, limit, offset):
        result = self.policies.items()
        if limit + offset > len(result):
            limit = len(result)
            offset = 0
        return result[offset:limit]

    def create(self, policy):
        id = policy.id
        with self.lock:
            if id in self.policies:
                raise PolicyExists
            self.policies[id] = policy

    def update(self, policy):
        self.policies[policy.id] = policy

    def delete(self, id):
        del self.policies[id]

    def find_by_request(self, request):
        with self.lock:
            return [p for p in self.policies if request.subject in p.subjects]
