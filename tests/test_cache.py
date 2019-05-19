from unittest.mock import Mock

from vakt.storage.memory import MemoryStorage
from vakt.storage.mongo import MongoStorage
from vakt import Policy
from vakt.cache import EnfoldCache


class TestEnfoldCache:

    def test_init_false(self):
        cache = MemoryStorage()
        policies = [Policy(1), Policy(2), Policy(3)]
        back = Mock(spec=MongoStorage, **{'get_all.return_value': [policies]})
        c = EnfoldCache(back, cache=cache, init=False)
        assert not back.get_all.called
        assert [] == c.cache.get_all(10000, 0)

    def test_init_true(self):
        cache = MemoryStorage()
        policies = [Policy(1), Policy(2), Policy(3)]
        back = Mock(spec=MongoStorage, **{'get_all.side_effect': [policies, []]})
        c = EnfoldCache(back, cache=cache, init=True)
        assert policies == c.cache.get_all(10000, 0)
