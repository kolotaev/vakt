import pytest
from operator import attrgetter

from vakt.storage.memory import MemoryStorage
from vakt.policy import Policy


class TestMemoryStorageYielding(MemoryStorage):
    def get_all(self, limit, offset):
        self._check_limit_and_offset(limit, offset)
        result = [v for v in self.policies.values()]
        if offset > len(result) or limit == 0:
            return []
        for p in result[offset:limit+offset]:
            yield p


@pytest.mark.parametrize('st', [
    MemoryStorage(),
    TestMemoryStorageYielding(),
])
def test_retrieve_all_for_returning_storage(st):
    st.add(Policy('a'))
    st.add(Policy('b'))
    st.add(Policy('c'))
    st.add(Policy('d'))
    st.add(Policy('e'))
    expected_ids = ['a', 'b', 'c', 'd', 'e']
    for i in range(1, 55):
        result = st.retrieve_all(i)
        result = list(result)
        assert 5 == len(result)
        assert expected_ids == sorted(map(attrgetter('uid'), result))
    # test batch is 0
    assert 0 == len(list(st.retrieve_all(0)))
    # test no batch specified
    res = list(st.retrieve_all())
    assert 5 == len(res)
    assert expected_ids == sorted(map(attrgetter('uid'), res))
    # test too big batch
    res = list(st.retrieve_all(100000))
    assert 5 == len(res)
    assert expected_ids == sorted(map(attrgetter('uid'), res))
