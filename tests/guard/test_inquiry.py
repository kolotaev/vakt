import pytest

from vakt.guard import Inquiry


def test_default_values():
    i = Inquiry()
    assert '' == i.subject
    assert '' == i.action
    assert '' == i.resource
    assert {} == i.context


def test_json_roundtrip():
    i = Inquiry(resource='books:abc', action='view', subject='bobby', context={'ip': '127.0.0.1'})
    s = i.to_json()
    r1 = Inquiry.from_json(s)
    assert 'books:abc' == r1.resource
    assert 'view' == r1.action
    assert 'bobby' == r1.subject
    assert {'ip': '127.0.0.1'} == r1.context


def test_json_decode_fails_for_incorrect_data():
    with pytest.raises(ValueError):
        Inquiry.from_json('{')


def test_can_create_empty_inquiry():
    i = Inquiry()
    assert isinstance(i, Inquiry)
    i2 = Inquiry.from_json('{}')
    assert isinstance(i2, Inquiry)


def test_pretty_print():
    i = Inquiry(resource='books:abc', action='view', context={'ip': '127.0.0.1'})
    assert "<class 'vakt.guard.Inquiry'>" in str(i)
    assert "'resource': 'books:abc'" in str(i)
    assert "'action': 'view'" in str(i)
    assert "'context': {'ip': '127.0.0.1'}" in str(i)


@pytest.mark.parametrize('first, second, must_equal', [
    (
        Inquiry(resource='books:abc', action='view', context={'ip': '127.0.0.1'}),
        Inquiry(action='view', resource='books:abc', context={'ip': '127.0.0.1'}),
        True,
    ),
    (
        Inquiry(action='view', resource='books:abc', context={'ip': '127.0.0.1'}),
        Inquiry(resource='books:абс', action='view', context={'ip': '127.0.0.1'}),
        False,
    ),
    (
        Inquiry(resource='books:абс', action='view', context={'ip': '127.0.0.1'}),
        Inquiry(resource='books:абс', action='view', context={'ip': '127.0.0.1'}),
        True,
    ),
    (
        Inquiry(),
        Inquiry(),
        True,
    ),
    (
        Inquiry(resource={'name': 'books:абс', 'loc': 'bar'},
                subject={'id': 123, 'teams': (123, 789, '145')},
                action={'name': 'view'},
                context={'ip': '127.0.0.1'}),
        Inquiry(resource={'name': 'books:абс', 'loc': 'bar'},
                subject={'id': 123, 'teams': (123, 789, '145')},
                action={'name': 'view'},
                context={'ip': '127.0.0.1'}),
        True,
    ),
    (
        Inquiry(resource={'name': 'books:абс', 'loc': 'bar'},
                subject={'id': 123, 'teams': (123, 789, '145')},
                action={'name': 'view'},
                context={'ip': '127.0.0.1'}),
        Inquiry(resource={'name': 'books:абс', 'loc': 'bar'},
                subject={'id': 123, 'teams': 'str'},
                action={'name': 'view'},
                context={'ip': '127.0.0.1'}),
        False,
    ),
    (
        Inquiry(resource={}, subject={}, action={}, context={}),
        Inquiry(context={}, subject={}, action={}, resource={}),
        True,
    ),
    (
        Inquiry(resource={'a': 'b', 'c': 'd'}, subject={'a': [1, 2, 3]}, action={}, context={}),
        Inquiry(context={}, subject={'a': [1, 2, 3]}, action={}, resource={'c': 'd', 'a': 'b'}),
        True,
    ),
])
def test_equals_and_equals_by_hash(first, second, must_equal):
    if must_equal:
        assert first == second
        assert hash(first) == hash(second)
    else:
        assert first != second
        assert hash(first) != hash(second)
