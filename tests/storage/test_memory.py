import pytest

from vakt.storage.memory import MemoryStorage
from vakt.policy import Policy
from vakt.guard import Inquiry
from vakt.exceptions import PolicyExistsError
from vakt.rules.operator import Eq
from vakt.rules.logic import Any


@pytest.fixture
def st():
    return MemoryStorage()


def test_add(st):
    st.add(Policy('1', description='foo'))
    assert '1' == st.get('1').uid
    assert 'foo' == st.get('1').description
    st.add(Policy('2', actions=[Eq('get'), Eq('put')], subjects=[Any()], resources=[{'books': Eq('Harry')}]))
    assert '2' == st.get('2').uid
    assert 2 == len(st.get('2').actions)
    assert 1 == len(st.get('2').subjects)
    assert isinstance(st.get('2').subjects[0], Any)
    assert 1 == len(st.get('2').resources)
    assert isinstance(st.get('2').resources[0]['books'], Eq)
    assert 'Harry' == st.get('2').resources[0]['books'].val


def test_policy_create_existing(st):
    st.add(Policy('1', description='foo'))
    with pytest.raises(PolicyExistsError):
        st.add(Policy('1', description='bar'))


def test_get(st):
    st.add(Policy('1'))
    st.add(Policy(2, description='some text'))
    assert isinstance(st.get('1'), Policy)
    assert '1' == st.get('1').uid
    assert 2 == st.get(2).uid
    assert 'some text' == st.get(2).description


@pytest.mark.parametrize('limit, offset, result', [
    (500, 0, 200),
    (101, 1, 101),
    (500, 50, 150),
    (200, 0, 200),
    (200, 1, 199),
    (199, 0, 199),
    (200, 50, 150),
    (0, 0, 0),
    (0, 100, 0),
    (1, 0, 1),
    (5, 4, 5),
    (200, 300, 0),
    (10000, 0, 200),
    (5, 198, 2),
    (5, 199, 1),
    (5, 200, 0),
    (5, 201, 0),
])
def test_get_all(st, limit, offset, result):
    for i in range(200):
        st.add(Policy(str(i)))
    assert result == len(st.get_all(limit, offset))


def test_get_all_check_policy_properties(st):
    st.add(Policy('1', description='foo'))
    assert 1 == len(st.get_all(100, 0))
    assert '1' == st.get_all(100, 0)[0].uid
    assert 'foo' == st.get_all(100, 0)[0].description


def test_get_all_with_incorrect_args(st):
    with pytest.raises(ValueError) as e:
        st.get_all(-1, 90)
    assert "Limit can't be negative" == str(e.value)

    with pytest.raises(ValueError) as e:
        st.get_all(0, -34)
    assert "Offset can't be negative" == str(e.value)


def test_find_for_inquiry(st):
    st.add(Policy('1', subjects=['max', 'bob']))
    st.add(Policy('2', subjects=['sam', 'nina']))
    st.add(Policy('3', subjects=[Eq('max'), Eq('bob')]))
    inquiry = Inquiry(subject='sam', action='get', resource='books')
    found = st.find_for_inquiry(inquiry)
    found = list(found)
    assert 3 == len(found)
    assert ['max', 'bob'] == found[0].subjects or \
           ['max', 'bob'] == found[1].subjects or \
           ['max', 'bob'] == found[2].subjects


def test_update(st):
    policy = Policy('1')
    st.add(policy)
    assert '1' == st.get('1').uid
    assert None is st.get('1').description
    policy.description = 'foo'
    st.update(policy)
    assert '1' == st.get('1').uid
    assert 'foo' == st.get('1').description
    p = Policy(2, actions=[Any()], subjects=[Eq('max'), Eq('bob')])
    st.add(p)
    assert 2 == st.get(2).uid
    p.actions = [Eq('get')]
    st.update(p)
    assert 1 == len(st.get(2).actions)
    assert 'get' == st.get(2).actions[0].val


def test_update_non_existing_does_not_create_anything(st):
    uid = str('1234567890_non_existent')
    st.update(Policy(uid, actions=['get'], description='bar'))
    assert st.get(uid) is None


def test_delete(st):
    policy = Policy('1')
    st.add(policy)
    assert '1' == st.get('1').uid
    st.delete('1')
    assert None is st.get('1')
    st.delete('1000000')
