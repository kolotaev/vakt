"""
Caching mechanisms for vakt
"""

import logging
from functools import lru_cache
from abc import ABCMeta, abstractmethod

from .storage.observable import ObservableMutationStorage
from .util import Observer
from .guard import Guard


__all__ = [
    'create_cached_guard',
    'EnfoldCache',
    'AllowanceCacheBackend',
]


log = logging.getLogger(__name__)


def create_cached_guard(storage, checker, cache=None, **kwargs):
    """
    Creates Guard whose `is_allowed` method calls are cached.
    It helps to increase performance for similar Inquiries in case you have static Policies set.

    :argument
    storage - Storage, that will be used by Guard and modified for further usage
    checker - Checker implementation, that will be used by Guard
    cache - argument allows you to provide your own cache implementation that must
            implement vakt.cache.AllowanceCacheBackend. If it is None the default in-memory LRU cache will be used.
            It also accepts optional keyword arguments that will be passed to a cache.
            Currently only `maxsize` is available.
    maxsize - argument allows you to specify a maximum size of a default in-memory LRU cache, (preferably a power of 2)

    :return (storage, guard, cache)
    guard - Guard whose `is_allowed` method will be cached
    storage - must be used in the code after the function call - it's an observable wrapper of the initial Storage.
              If you are not interacting with policies through this Storage cache won't behave correctly.
    cache - AllowanceCache that can be used to obtain information about a cache state
    """
    st = ObservableMutationStorage(storage)
    guard = Guard(st, checker)
    cache = AllowanceCache(guard, cache_backend=cache, **kwargs)
    st.add_listener(cache)
    return guard, st, cache


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
        self.populate_step_size = 1000
        if populate:
            self.populate()

    def populate(self):
        for p in self.storage.retrieve_all(self.populate_step_size):
            self.cache.add(p)

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
        result = list(self.cache.get_all(limit, offset))
        if len(result) > 0:
            return result
        return self.storage.get_all(limit, offset)

    def retrieve_all(self, *args, **kwargs):
        """
        Cache storage `retrieve_all`
        """
        result = list(self.cache.retrieve_all(*args, **kwargs))
        if len(result) > 0:
            return result
        return self.storage.retrieve_all(*args, **kwargs)

    def find_for_inquiry(self, inquiry, checker=None):
        """
        Cache storage `find_for_inquiry`
        """
        result = list(self.cache.find_for_inquiry(inquiry, checker))
        if len(result) > 0:
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


class AllowanceCache(Observer):
    """
    Caches hits of `is_allowed` (technically, its more tiny part: `is_allowed_check`) for a given Inquiry.
    In case of a cache hit returns the cached boolean result, in case of a cache miss goes to a Storage and
    memorizes its result for future calls with the same Inquiry.
    If underlying Storage notifies it that policy-set was anyhow changed, invalidates all the cached results.

    You need to pass proper options in order to create cache of a desired type.
    Available options are:
    maxsize - maximum size of a cache
    backend - which backend will be used for caching
    type - type of a caching algorithm to be used
    """
    def __init__(self, guard, cache_backend=None, **kwargs):
        self.options = kwargs
        if cache_backend is None:
            self.cache = LRUCache(maxsize=self.options['maxsize'])
        guard.is_allowed_check = self.cache.wrap(guard.is_allowed_check)

    def update(self):
        """
        Is a callback for fire events on Storage modify actions.
        We need to invalidate cache since policy set is changed with each add/delete/update storage action,
        thus old Guard answers on inquiries are will be no longer valid.
        """
        self.cache.invalidate()

    def info(self):
        """
        Get information about current cache.
        """
        return self.cache.info()


class AllowanceCacheBackend(metaclass=ABCMeta):
    """
    Interface for backed cache implementations for AllowanceCache.
    All implementations should subclass it.
    """
    @abstractmethod
    def wrap(self, func):
        """
        Wrap function into its cached version and return it.
        """
        pass

    @abstractmethod
    def invalidate(self):
        """
        Invalidate the cache
        """
        pass

    @abstractmethod
    def info(self):
        """
        Get cache information.
        Preferably it should be an object with attributes:
        - hits - number of cache hits,
        - misses - number of cache misses,
        - maxsize - maximum number of elements the cache can contain,
        - currsize - number of elements the cache contains at the moment
        - ... some other useful attributes
        """
        pass


class LRUCache(AllowanceCacheBackend):
    """
    Std lib LRU in-memory cache.
    """
    def __init__(self, **kwargs):
        self.maxsize = kwargs['maxsize']
        self._wrapped_func = None

    def wrap(self, func):
        self._wrapped_func = lru_cache(self.maxsize)(func)
        return self._wrapped_func

    def invalidate(self):
        self._wrapped_func.cache_clear()

    def info(self):
        return self._wrapped_func.cache_info()
