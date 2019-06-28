"""
Caching mechanisms for vakt
"""

import logging
from functools import lru_cache

from .storage.observable import ObservableMutationStorage
from .util import Observer


__all__ = [
    'EnfoldCache',
    'GuardCache',
]


log = logging.getLogger(__name__)


class EnfoldCache:
    """
    Wraps all underlying storage interface calls with a cache that is represented by another storage.
    By default `populate` arg is True and thus it populates cache with all the existing policies at the startup.
    This may take a long time depending on the size of policies set n your backend storage.
    Otherwise you need to set `populate` arg is False and manually call ec.populate()
    before you start working with the cache.

    Typical (and recommended) usage is:
    storage = EnfoldCache(MongoStorage(...), cache=MemoryStorage())

    Or it might be:
    storage = EnfoldCache(MongoStorage(...), cache=MemoryStorage(), populate=False)
    ...
    storage.populate()
    """

    def __init__(self, storage, cache, populate=True):
        self.storage = storage
        self.cache = cache
        self.populate_step = 1000
        self._get_all_fetched = False
        if populate:
            self.populate()

    def populate(self):
        limit = self.populate_step
        offset = 0
        while True:
            policies = self.storage.get_all(limit, offset)
            if not policies:
                break
            for p in policies:
                self.cache.add(p)
            offset = limit + 1

    def add(self, policy):
        """
        Cache storage `add`
        """
        # we aren't catching any exceptions - just letting them pass
        res = self.storage.add(policy)
        self.cache.add(policy)
        return res

    def get(self, uid):
        """
        Cache storage `get`
        """
        policy = self.cache.get(uid)
        if policy:
            return policy
        log.warning(
            '%s cache miss for get Policy with UID=%s. Trying to get it from backend storage',
            type(self).__name__, uid
        )
        return self.storage.get(uid)

    def get_all(self, limit, offset):
        """
        Cache storage `get_all`
        """
        result = self.cache.get_all(limit, offset)
        if result:
            return result
        return self.storage.get_all(limit, offset)

    def find_for_inquiry(self, inquiry, checker=None):
        """
        Cache storage `find_for_inquiry`
        """
        result = self.cache.find_for_inquiry(inquiry, checker)
        if result:
            return result
        log.warning('%s cache miss for find_for_inquiry. Trying it from backend storage', type(self).__name__)
        return self.storage.find_for_inquiry(inquiry, checker)

    def update(self, policy):
        """
        Cache storage `update`
        """
        res = self.storage.update(policy)
        self.cache.update(policy)
        return res

    def delete(self, uid):
        """
        Cache storage `delete`
        """
        res = self.storage.delete(uid)
        self.cache.delete(uid)
        return res


class GuardCache(Observer):
    """
    Caches hits of `find_for_inquiry` for given Inquiry and Checker.
    In case of a cache hit returns the cached boolean result, in case of a cache miss goes to a Storage and
    memorizes its result for future calls with the same Inquiry and Checker.
    If underlying Storage notifies it that policies set was anyhow changed, invalidates all the cached results.
    """
    def __init__(self, storage, maxsize=None, cache_type='memory'):
        self.storage = ObservableMutationStorage(storage)
        self.cache_type = cache_type
        self.maxsize = maxsize
        self.cache = self._create_cache()
        # self._original_find_for_inquiry = None

    def wrap(self):
        self.storage.add_listener(self)
        # self._original_find_for_inquiry = self.storage.find_for_inquiry
        self.storage.find_for_inquiry = self.cache.wrap(self.storage.find_for_inquiry)
        return self.storage

    # todo - we need hashable args
    # def find_for_inquiry(self, inquiry, checker=None):
    #     inq_hash = inquiry.to_json()
    #     checker_hash = type(checker)
    #     return self.storage.find_for_inquiry

    def update(self):
        """
        Is a callback for fire events on Storage modify actions.
        We need to invalidate cache since policy set is changed with each add/delete/update storage action,
        thus old Guard answers on inquiries are will be no longer valid.
        """
        self.cache.invalidate()

    def _create_cache(self):
        if self.cache_type == 'memory':
            return LRUCache(maxsize=self.maxsize)
        else:
            raise AttributeError('Unknown cache type for GuardCache')


# ###############################################
# Underlying cache implementations for GuardCache

class LRUCache:
    def __init__(self, **kwargs):
        self.maxsize = kwargs['maxsize']
        self._wrapped_func = None

    def wrap(self, func):
        self._wrapped_func = lru_cache(self.maxsize)(func)
        return self._wrapped_func

    def invalidate(self):
        self._wrapped_func.cache_clear()

    def info(self):
        self._wrapped_func.cache_info()
