from unittest.mock import Mock, patch

import pytest

from vakt.storage.memory import MemoryStorage
from vakt.storage.mongo import MongoStorage
from vakt import Policy, Inquiry, RulesChecker, ALLOW_ACCESS, Guard
from vakt.cache import AllowanceCache
from vakt.exceptions import PolicyExistsError
from vakt.rules import Eq
from vakt.guard import create_guard


class TestGuardCache:

    def test_hashable_args(self):
        chk = RulesChecker()
        storage = MemoryStorage()
        cache = AllowanceCache(Guard(storage, chk), maxsize=256)
        guard = cache.guard
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
        assert 4 == cache.info().hits
        assert 2 == cache.info().misses
        assert 2 == cache.info().currsize
