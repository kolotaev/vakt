from unittest.mock import Mock, patch

import pytest

from vakt.storage.memory import MemoryStorage
from vakt.storage.mongo import MongoStorage
from vakt import Policy, Inquiry, RulesChecker
from vakt.cache import EnfoldCache
from vakt.exceptions import PolicyExistsError
from ..helper import MemoryStorageYieldingExample2


class TestEnfoldCache:

    def test_init_without_populate(self):
        cache = MemoryStorage()
        policies = [Policy(1), Policy(2), Policy(3)]
        back = Mock(spec=MongoStorage, **{'retrieve_all.return_value': [policies]})
        c = EnfoldCache(back, cache=cache, populate=False)
        assert not back.retrieve_all.called
        assert [] == c.cache.get_all(1000, 0)

    def test_init_with_populate_and_populate_is_true_by_default(self):
        cache = MemoryStorage()
        policies = [Policy(1), Policy(2), Policy(3)]
        back = Mock(spec=MongoStorage, **{'retrieve_all.side_effect': [policies], 'get_all.side_effect': []})
        ec = EnfoldCache(back, cache=cache)
        assert back.retrieve_all.called
        assert policies == ec.cache.get_all(10000, 0)

    def test_init_with_populate_for_dirty_cache_storage(self):
        cache = MemoryStorage()
        cache.add(Policy(1))
        policies = [Policy(1), Policy(2), Policy(3)]
        back = Mock(spec=MongoStorage, **{'retrieve_all.side_effect': [policies]})
        with pytest.raises(Exception) as excinfo:
            EnfoldCache(back, cache=cache, populate=True)
        assert 'Conflicting UID = 1' == str(excinfo.value)
        assert back.retrieve_all.called

    def test_add_return_value(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        backend_return = back_storage.add(Policy(1))
        ec_return = ec.add(Policy(2))
        assert backend_return == ec_return

    def test_add_ok(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1)
        p2 = Policy(2)
        p3 = Policy(3)
        ec.add(p1)
        assert [p1] == cache_storage.get_all(100, 0)
        assert [p1] == back_storage.get_all(100, 0)
        ec.add(p2)
        ec.add(p3)
        assert [p1, p2, p3] == cache_storage.get_all(100, 0)
        assert [p1, p2, p3] == back_storage.get_all(100, 0)

    def test_add_fail(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1)
        p2 = Policy(2)
        p3 = Policy(3)
        ec.add(p1)
        back_storage.add = Mock(side_effect=PolicyExistsError('2'))
        with pytest.raises(PolicyExistsError) as excinfo:
            ec.add(p2)
        assert 'Conflicting UID = 2' == str(excinfo.value)
        assert [p1] == back_storage.get_all(1000, 0)
        # test general exception
        back_storage.add = Mock(side_effect=Exception('foo'))
        with pytest.raises(Exception) as excinfo:
            ec.add(p3)
        assert 'foo' == str(excinfo.value)
        assert [p1] == back_storage.get_all(1000, 0)
        assert [p1] == cache_storage.get_all(1000, 0)

    def test_update_return_value(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1, description='foo')
        ec.add(p1)
        p1.description = 'foo upd'
        backend_return = back_storage.update(p1)
        ec_return = ec.update(p1)
        assert backend_return == ec_return

    def test_update_ok(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1, description='foo')
        p2 = Policy(2, description='bar')
        p3 = Policy(3, description='baz')
        ec.add(p1)
        ec.add(p2)
        ec.add(p3)
        p1.description = 'foo2'
        ec.update(p1)
        p2.description = 'bar2'
        ec.update(p2)
        assert [p1, p2, p3] == cache_storage.get_all(100, 0)
        assert [p1, p2, p3] == back_storage.get_all(100, 0)

    def test_update_fail(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1, description='foo')
        p2 = Policy(2, description='bar')
        ec.add(p1)
        ec.add(p2)
        back_storage.update = Mock(side_effect=Exception('error!'))
        with pytest.raises(Exception) as excinfo:
            p1.description = 'changed foo'
            ec.update(p1)
        assert 'error!' == str(excinfo.value)
        assert [p1, p2] == back_storage.get_all(1000, 0)
        assert [p1, p2] == cache_storage.get_all(1000, 0)

    def test_delete_return_value(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1)
        ec.add(p1)
        backend_return = back_storage.delete(p1)
        ec_return = ec.delete(p1)
        assert backend_return == ec_return

    def test_delete_ok(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1, description='foo')
        p2 = Policy(2, description='bar')
        ec.add(p1)
        ec.add(p2)
        ec.delete(1)
        ec.delete(2)
        assert [] == cache_storage.get_all(100, 0)
        assert [] == back_storage.get_all(100, 0)

    def test_delete_fail(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1, description='foo')
        p2 = Policy(2, description='bar')
        ec.add(p1)
        ec.add(p2)
        back_storage.delete = Mock(side_effect=Exception('error!'))
        with pytest.raises(Exception) as excinfo:
            ec.delete(2)
        assert 'error!' == str(excinfo.value)
        assert [p1, p2] == back_storage.get_all(1000, 0)
        assert [p1, p2] == cache_storage.get_all(1000, 0)

    def test_get_return_value(self):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1)
        ec.add(p1)
        backend_return = back_storage.get(1)
        ec_return = ec.get(1)
        assert backend_return == ec_return

    @patch('vakt.cache.log')
    def test_get_for_non_populated_cache(self, log_mock):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        p1 = Policy(1, description='foo')
        p2 = Policy(2, description='bar')
        back_storage.add(p1)
        back_storage.add(p2)
        ec = EnfoldCache(back_storage, cache=cache_storage, populate=False)
        assert p1 == ec.get(1)
        log_mock.warning.assert_called_with(
            '%s cache miss for get Policy with UID=%s. Trying to get it from backend storage',
            'EnfoldCache',
            1
        )
        log_mock.reset_mock()
        assert p2 == ec.get(2)
        assert 1 == log_mock.warning.call_count
        log_mock.reset_mock()
        # test we won't return any inexistent policies
        assert ec.get(3) is None

    @patch('vakt.cache.log')
    def test_get_for_populated_cache(self, log_mock):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        p1 = Policy(1, description='foo')
        p2 = Policy(2, description='bar')
        back_storage.add(p1)
        back_storage.add(p2)
        ec = EnfoldCache(back_storage, cache=cache_storage, populate=True)
        assert p1 == ec.get(1)
        assert 0 == log_mock.warning.call_count
        log_mock.reset_mock()
        assert p2 == ec.get(2)
        assert 0 == log_mock.warning.call_count
        log_mock.reset_mock()
        # test we won't return any inexistent policies
        assert ec.get(3) is None
        log_mock.warning.assert_called_with(
            '%s cache miss for get Policy with UID=%s. Trying to get it from backend storage',
            'EnfoldCache',
            3
        )

    @pytest.mark.parametrize('storage', [
        MemoryStorage(),
        MemoryStorageYieldingExample2(),
    ])
    def test_get_all_return_value(self, storage):
        cache_storage = storage
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1)
        p2 = Policy(2)
        p3 = Policy(3)
        ec.add(p1)
        ec.add(p2)
        ec.add(p3)
        backend_return = back_storage.get_all(100, 0)
        ec_return = back_storage.get_all(100, 0)
        assert backend_return == ec_return

    @pytest.mark.parametrize('storage', [
        MemoryStorage(),
        MemoryStorageYieldingExample2(),
    ])
    def test_get_all(self, storage):
        p1 = Policy(1)
        p2 = Policy(2)
        p3 = Policy(3)
        p4 = Policy(4)
        p5 = Policy(5)
        cache_storage = storage
        back_storage = Mock(spec=MongoStorage, **{'get_all.return_value': []})
        ec = EnfoldCache(back_storage, cache=cache_storage, populate=False)
        assert [] == ec.get_all(1, 0)
        assert [] == ec.get_all(100, 0)
        # test we return from the backend
        back_storage.get_all = Mock(return_value=[p1, p2, p3])
        assert [p1, p2, p3] == list(ec.get_all(100, 0))
        back_storage.get_all = Mock(return_value=[])
        assert [] == list(ec.get_all(100, 0))
        # test we return from the cache
        cache_storage.add(p4)
        cache_storage.add(p5)
        back_storage.get_all = Mock(return_value=[p1, p2, p3])
        assert [p4] == list(ec.get_all(1, 0))
        assert [p5] == list(ec.get_all(1, 1))
        assert [p4, p5] == list(ec.get_all(2, 0))

    @pytest.mark.parametrize('storage', [
        MemoryStorage(),
        MemoryStorageYieldingExample2(),
    ])
    def test_retrieve_all_return_value(self, storage):
        cache_storage = storage
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        p1 = Policy(1)
        p2 = Policy(2)
        p3 = Policy(3)
        ec.add(p1)
        ec.add(p2)
        ec.add(p3)
        backend_return = back_storage.retrieve_all()
        ec_return = back_storage.retrieve_all()
        assert list(backend_return) == list(ec_return)

    @pytest.mark.parametrize('storage', [
        MemoryStorage(),
        MemoryStorageYieldingExample2(),
    ])
    def test_retrieve_all(self, storage):
        p1 = Policy(1)
        p2 = Policy(2)
        p3 = Policy(3)
        p4 = Policy(4)
        p5 = Policy(5)
        cache_storage = storage
        back_storage = Mock(spec=MongoStorage, **{'retrieve_all.return_value': []})
        ec = EnfoldCache(back_storage, cache=cache_storage, populate=False)
        assert [] == ec.retrieve_all()
        back_storage.retrieve_all.assert_called_with()
        assert [] == ec.retrieve_all(batch=10)
        back_storage.retrieve_all.assert_called_with(batch=10)
        assert [] == ec.retrieve_all(10)
        back_storage.retrieve_all.assert_called_with(10)
        # test we return from the backend
        back_storage.retrieve_all = Mock(return_value=[p1, p2, p3])
        assert [p1, p2, p3] == list(ec.retrieve_all())
        back_storage.retrieve_all = Mock(return_value=[])
        assert [] == list(ec.retrieve_all())
        # test we return from the cache (cache is dirty)
        cache_storage.add(p4)
        cache_storage.add(p5)
        back_storage.retrieve_all = Mock(return_value=[p1, p2, p3])
        assert [p4, p5] == list(ec.retrieve_all(1))
        assert [p4, p5] == list(ec.retrieve_all(batch=1))
        assert [p4, p5] == list(ec.retrieve_all())

    @pytest.mark.parametrize('storage', [
        MemoryStorage(),
        MemoryStorageYieldingExample2(),
    ])
    def test_find_for_inquiry_return_value(self, storage):
        cache_storage = storage
        back_storage = MemoryStorage()
        ec = EnfoldCache(back_storage, cache=cache_storage)
        inq = Inquiry(action='get')
        p1 = Policy(1)
        p2 = Policy(2)
        ec.add(p1)
        ec.add(p2)
        backend_return = back_storage.find_for_inquiry(inq)
        ec_return = ec.find_for_inquiry(inq)
        assert list(backend_return) == list(ec_return)

    @patch('vakt.cache.log')
    def test_find_for_inquiry_for_non_populated_cache(self, log_mock):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        inq = Inquiry(action='get')
        chk1 = RulesChecker()
        p1 = Policy(1, description='foo')
        p2 = Policy(2, description='bar')
        back_storage.add(p1)
        back_storage.add(p2)
        ec = EnfoldCache(back_storage, cache=cache_storage, populate=False)
        # Make first request
        assert [p1, p2] == list(ec.find_for_inquiry(inquiry=inq, checker=chk1))
        log_mock.warning.assert_called_with(
            '%s cache miss for find_for_inquiry. Trying it from backend storage', 'EnfoldCache'
        )
        log_mock.reset_mock()
        # Make second request
        assert [p1, p2] == list(ec.find_for_inquiry(inquiry=inq, checker=chk1))
        assert 1 == log_mock.warning.call_count
        log_mock.reset_mock()

    @patch('vakt.cache.log')
    def test_find_for_inquiry_for_populated_cache(self, log_mock):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        inq = Inquiry(action='get')
        chk1 = RulesChecker()
        p1 = Policy(1, description='foo')
        p2 = Policy(2, description='bar')
        cache_storage.add(p1)
        cache_storage.add(p2)
        ec = EnfoldCache(back_storage, cache=cache_storage, populate=True)
        # Make first request
        assert [p1, p2] == list(ec.find_for_inquiry(inquiry=inq, checker=chk1))
        assert 0 == log_mock.warning.call_count
        log_mock.reset_mock()
        # Make second request
        assert [p1, p2] == list(ec.find_for_inquiry(inquiry=inq, checker=chk1))
        assert 0 == log_mock.warning.call_count

    @patch('vakt.cache.log')
    def test_general_flow(self, log_mock):
        cache_storage = MemoryStorage()
        back_storage = MemoryStorage()
        inq = Inquiry(action='get')
        chk1 = RulesChecker()
        p1 = Policy(1, description='initial')
        p2 = Policy(2, description='initial')
        p3 = Policy(3, description='added later')
        # initialize backend storage
        back_storage.add(p1)
        back_storage.add(p2)
        # create enfold-cache but do not populate it
        ec = EnfoldCache(back_storage, cache=cache_storage, populate=False)
        # make sure policies are returned from the backend
        assert [p1, p2] == list(ec.find_for_inquiry(inquiry=inq, checker=chk1))
        # make sure we logged warning about cache miss
        log_mock.warning.assert_called_with(
            '%s cache miss for find_for_inquiry. Trying it from backend storage', 'EnfoldCache'
        )
        log_mock.reset_mock()
        # populate cache with backend policies so that we do not make cache hit misses
        ec.populate()
        # make sure policies are returned
        assert [p1, p2] == list(ec.find_for_inquiry(inquiry=inq, checker=chk1))
        # make sure we do not have cache misses
        assert 0 == log_mock.warning.call_count
        log_mock.reset_mock()
        # let's add a new policy via enfold-cache
        ec.add(p3)
        # make sure policies are returned
        assert [p1, p2, p3] == list(ec.find_for_inquiry(inquiry=inq, checker=chk1))
        # make sure we do not have cache misses
        assert 0 == log_mock.warning.call_count
        log_mock.reset_mock()
        # make sure we have those policies in the backend-storage
        assert [p1, p2, p3] == list(back_storage.find_for_inquiry(inquiry=inq, checker=chk1))
        # make sure we have those policies in the cache-storage
        assert [p1, p2, p3] == list(cache_storage.find_for_inquiry(inquiry=inq, checker=chk1))
        # -----------------------
        # -----------------------
        # -----------------------
        # let's re-create enfold cache. This time with initial population
        cache_storage2 = MemoryStorage()
        ec2 = EnfoldCache(back_storage, cache=cache_storage2, populate=True)
        # make sure we have all policies in the cache-storage
        assert [p1, p2, p3] == list(cache_storage2.find_for_inquiry(inquiry=inq, checker=chk1))
        # make sure policies are returned by find_for_inquiry
        assert [p1, p2, p3] == list(ec2.find_for_inquiry(inquiry=inq, checker=chk1))
        # make sure we do not have cache misses
        assert 0 == log_mock.warning.call_count
        log_mock.reset_mock()
