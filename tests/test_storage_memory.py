import pytest

from vakt.storage.memory import MemoryStorage
from vakt.policy import Policy
from vakt.guard import Inquiry
from vakt.exceptions import PolicyExistsError


@pytest.fixture
def st():
    return MemoryStorage()


def test_add(st):
    st.add(Policy('1', description='foo'))
    assert '1' == st.get('1').id
    assert 'foo' == st.get('1').description


def test_policy_create_existing(st):
    st.add(Policy('1', description='foo'))
    with pytest.raises(PolicyExistsError):
        st.add(Policy('1', description='bar'))


def test_get(st):
    st.add(Policy('1'))
    st.add(Policy(2, description='some text'))
    assert isinstance(st.get('1'), Policy)
    assert '1' == st.get('1').id
    assert 2 == st.get(2).id
    assert 'some text' == st.get(2).description


def test_get_all(st):
    for i in range(200):
        st.add(Policy(str(i)))
    assert 200 == len(st.get_all(500, 0))
    assert 200 == len(st.get_all(500, 50))
    assert 200 == len(st.get_all(200, 0))
    assert 200 == len(st.get_all(200, 1))
    assert 199 == len(st.get_all(199, 0))
    assert 200 == len(st.get_all(200, 50))

    assert 1 == len(st.get_all(1, 0))

    assert 5 == len(st.get_all(5, 4))


def test_get_all_for_one(st):
    st.add(Policy('1', description='foo'))
    assert 1 == len(st.get_all(100, 0))
    assert '1' == st.get_all(100, 0)[0].id
    assert 'foo' == st.get_all(100, 0)[0].description


def test_find_for_inquiry(st):
    st.add(Policy('1', subjects=['max', 'bob']))
    st.add(Policy('2', subjects=['sam', 'nina']))
    inquiry = Inquiry(subject='sam', action='get', resource='books')
    found = st.find_for_inquiry(inquiry)
    assert 2 == len(found)
    assert ['max', 'bob'] == found[0].subjects or ['max', 'bob'] == found[1].subjects


def test_update(st):
    policy = Policy('1')
    st.add(policy)
    assert '1' == st.get('1').id
    assert None is st.get('1').description
    policy.description = 'foo'
    st.update(policy)
    assert '1' == st.get('1').id
    assert 'foo' == st.get('1').description


def test_delete(st):
    policy = Policy('1')
    st.add(policy)
    assert '1' == st.get('1').id
    st.delete('1')
    assert None is st.get('1')
    st.delete('1000000')
