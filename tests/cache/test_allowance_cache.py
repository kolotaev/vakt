from vakt.storage.memory import MemoryStorage
from vakt import Policy, Inquiry, RulesChecker, ALLOW_ACCESS
from vakt.cache import create_cached_guard
from vakt.rules import Eq


class TestAllowanceCache:

    def test_same_inquiries_are_cached(self):
        storage, guard, cache = create_cached_guard(MemoryStorage(), RulesChecker(), maxsize=256)
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

    def test_cache_is_invalidated_on_policy_change(self):
        inq1 = Inquiry(action='get', resource='book', subject='Max')
        inq2 = Inquiry(action='get', resource='book', subject='Jim')
        storage, guard, cache = create_cached_guard(MemoryStorage(), RulesChecker(), maxsize=256)
        p1 = Policy(1, actions=[Eq('get')], resources=[Eq('book')], subjects=[Eq('Max')], effect=ALLOW_ACCESS)
        storage.add(p1)
        assert guard.is_allowed(inq1)
        assert guard.is_allowed(inq1)
        assert 1 == cache.info().hits
        p1.subjects = [Eq('Jim')]
        storage.update(p1)
        assert not guard.is_allowed(inq1)
        assert not guard.is_allowed(inq1)
        assert guard.is_allowed(inq2)
        assert guard.is_allowed(inq2)
        # assert 2 == cache.info().hits

