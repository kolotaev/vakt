"""
File storage for Policies.
"""

import logging

from ..storage.abc import Storage
from ..storage.memory import MemoryStorage
from ..readers import YamlReader, JSONReader


log = logging.getLogger(__name__)


class FileStorage(Storage):
    """
    Reads all policies from file and keeps them in the backing Storage (in memory by default).
    """
    def __init__(self, file, storage=None):
        if storage is None:
            self.back_store = MemoryStorage()
        reader = None
        for reader_cls in [JSONReader, YamlReader]:
            try:
                reader = reader_cls(file)
                if reader:
                    break
            except Exception:
                pass
        if not reader:
            raise RuntimeError('Failed to created reader from file %s', file)
        for p in reader.read():
            self.back_store.add(p)

    def add(self, policy):
        raise NotImplementedError('Please, add Policy in file manually')

    def get(self, uid):
        return self.back_store.get(uid)

    def get_all(self, limit, offset):
        return self.back_store.get_all(limit, offset)

    def find_for_inquiry(self, inquiry, checker=None):
        return self.back_store.find_for_inquiry(inquiry, checker)

    def update(self, policy):
        raise NotImplementedError('Please, update Policy in file manually')

    def delete(self, uid):
        raise NotImplementedError('Please, delete Policy in file manually')
