from unittest.mock import Mock, patch

import pytest

from vakt.storage.memory import MemoryStorage
from vakt.storage.mongo import MongoStorage
from vakt import Policy
from vakt.cache import EnfoldCache
from vakt.exceptions import PolicyExistsError


class TestEnfoldCache:

    def test_init_with_populate_false(self):
        cache = MemoryStorage()
        policies = [Policy(1), Policy(2), Policy(3)]
        back = Mock(spec=MongoStorage, **{'get_all.return_value': [policies]})
        c = EnfoldCache(back, cache=cache, populate=False)
        assert not back.get_all.called
        assert [] == c.cache.get_all(1000, 0)

    def test_init_with_populate_true(self):
        cache = MemoryStorage()
        policies = [Policy(1), Policy(2), Policy(3)]
        back = Mock(spec=MongoStorage, **{'get_all.side_effect': [policies, []]})
        ec = EnfoldCache(back, cache=cache, populate=True)
        assert policies == ec.cache.get_all(1000, 0)

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
        ec = EnfoldCache(back_storage, cache=cache_storage)
        assert p1 == ec.get(1)
        log_mock.warning.assert_called_with(
            '%s cache miss for get Policy with UID=%s. Trying to get it from backend storage',
            'EnfoldCache',
            1
        )
        log_mock.reset_mock()
        assert p2 == ec.get(2)
        log_mock.warning.assert_called()
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
