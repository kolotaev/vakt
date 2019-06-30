from unittest.mock import Mock, patch

import pytest

from vakt.storage.memory import MemoryStorage
from vakt.storage.mongo import MongoStorage
from vakt import Policy, Inquiry, RulesChecker, ALLOW_ACCESS, Guard
from vakt.guard import CachedGuard
from vakt.cache import AllowanceCache
from vakt.exceptions import PolicyExistsError
from vakt.rules import Eq


class TestAllowanceCache:

    def test_hashable_args(self):
        chk = RulesChecker()
        storage = MemoryStorage()
        # cache = AllowanceCache(Guard(storage, chk), maxsize=256)
        guard = CachedGuard(storage, chk, maxsize=256)
        # cache = guard.cache
        p1 = Policy(1, actions=[Eq('get')], resources=[Eq('book')], subjects=[Eq('Max')], effect=ALLOW_ACCESS)
        storage.add(p1)
        inq1 = Inquiry(action='get', resource='book', subject='Max')
        inq2 = Inquiry(action='get', resource='book', subject='Jamey')
        assert guard.is_allowed(inq1)
        assert guard.is_allowed(inq1)
        assert guard.is_allowed(inq1)
        assert guard.is_allowed(inq1)
        assert guard.is_allowed(inq1)
        assert not guard.is_allowed(inq2)
        assert 4 == guard.cache.info().hits
        assert 2 == guard.cache.info().misses
        assert 2 == guard.cache.info().currsize
