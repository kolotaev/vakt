import pytest

from vakt.managers.memory import MemoryManager
from vakt.policy import DefaultPolicy
from vakt.guard import Request
from vakt.exceptions import PolicyExists


@pytest.fixture
def pm():
    return MemoryManager()


def test_create(pm):
    pm.create(DefaultPolicy('1', description='foo'))
    assert '1' == pm.get('1').id
    assert 'foo' == pm.get('1').description


def test_policy_create_existing(pm):
    pm.create(DefaultPolicy('1', description='foo'))
    with pytest.raises(PolicyExists):
        pm.create(DefaultPolicy('1', description='bar'))


def test_get(pm):
    pm.create(DefaultPolicy('1'))
    pm.create(DefaultPolicy(2, description='some text'))
    assert isinstance(pm.get('1'), DefaultPolicy)
    assert '1' == pm.get('1').id
    assert 2 == pm.get(2).id
    assert 'some text' == pm.get(2).description


def test_get_all(pm):
    for i in range(200):
        pm.create(DefaultPolicy(str(i)))
    assert 200 == len(pm.get_all(500, 0))
    assert 200 == len(pm.get_all(500, 50))
    assert 200 == len(pm.get_all(200, 0))
    assert 200 == len(pm.get_all(200, 1))
    assert 199 == len(pm.get_all(199, 0))
    assert 200 == len(pm.get_all(200, 50))

    assert 1 == len(pm.get_all(1, 0))

    assert 5 == len(pm.get_all(5, 4))


def test_get_all_for_one(pm):
    pm.create(DefaultPolicy('1', description='foo'))
    assert 1 == len(pm.get_all(100, 0))
    assert '1' == pm.get_all(100, 0)[0].id
    assert 'foo' == pm.get_all(100, 0)[0].description


def test_find_by_request(pm):
    pm.create(DefaultPolicy('1', subjects=['max', 'bob']))
    pm.create(DefaultPolicy('2', subjects=['sam', 'nina']))
    req = Request(subject='sam', action='get', resource='books')
    found = pm.find_by_request(req)
    assert 2 == len(found)
    assert ['max', 'bob'] == found[0].subjects or ['max', 'bob'] == found[1].subjects


def test_update(pm):
    policy = DefaultPolicy('1')
    pm.create(policy)
    assert '1' == pm.get('1').id
    assert None is pm.get('1').description
    policy.description = 'foo'
    pm.update(policy)
    assert '1' == pm.get('1').id
    assert 'foo' == pm.get('1').description


def test_delete(pm):
    policy = DefaultPolicy('1')
    pm.create(policy)
    assert '1' == pm.get('1').id
    pm.delete('1')
    assert None is pm.get('1')
    pm.delete('1000000')
