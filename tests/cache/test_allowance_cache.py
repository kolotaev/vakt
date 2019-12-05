from vakt.storage.memory import MemoryStorage
from vakt import Policy, Inquiry, RulesChecker, ALLOW_ACCESS
from vakt.cache import create_cached_guard
from vakt.rules import Eq


class TestAllowanceCache:

    def test_same_inquiries_are_cached(self):
        guard, storage, cache = create_cached_guard(MemoryStorage(), RulesChecker(), maxsize=256)
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
        def assert_after_modification():
            assert 0 == cache.info().hits
            assert 0 == cache.info().misses
            assert 0 == cache.info().currsize
            assert not guard.is_allowed(inq1)
            assert not guard.is_allowed(inq1)
            assert guard.is_allowed(inq2)
            assert guard.is_allowed(inq2)
            assert guard.is_allowed(inq2)
            assert 3 == cache.info().hits
            assert 2 == cache.info().misses
            assert 2 == cache.info().currsize

        inq1 = Inquiry(action='get', resource='book', subject='Max')
        inq2 = Inquiry(action='get', resource='book', subject='Jim')
        guard, storage, cache = create_cached_guard(MemoryStorage(), RulesChecker(), maxsize=256)
        p1 = Policy(1, actions=[Eq('get')], resources=[Eq('book')], subjects=[Eq('Max')], effect=ALLOW_ACCESS)
        p2 = Policy(2, actions=[Eq('get')], resources=[Eq('magazine')], subjects=[Eq('Max')], effect=ALLOW_ACCESS)
        storage.add(p1)
        assert guard.is_allowed(inq1)
        assert guard.is_allowed(inq1)
        assert 1 == cache.info().hits
        assert 1 == cache.info().misses
        assert 1 == cache.info().currsize
        # start modifications
        p1.subjects = [Eq('Jim')]
        storage.update(p1)
        assert_after_modification()
        storage.add(p2)
        assert_after_modification()
        storage.delete(p2)
        assert_after_modification()
