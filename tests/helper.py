from vakt.storage.memory import MemoryStorage
from vakt.util import Observer


# todo - move all helper and unit-test example classes and functions here

class MemoryStorageYieldingExample(MemoryStorage):
    def get_all(self, limit, offset):
        self._check_limit_and_offset(limit, offset)
        result = [v for v in self.policies.values()]
        if offset > len(result) or limit == 0:
            return []
        for p in result[offset:limit+offset]:
            yield p


class MemoryStorageYieldingExample2(MemoryStorageYieldingExample):
    def find_for_inquiry(self, inquiry, checker=None):
        for p in super().find_for_inquiry(inquiry, checker):
            yield p


class CountObserver(Observer):
    def __init__(self):
        self.count = 0

    def update(self):
        self.count += 1
