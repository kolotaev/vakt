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


def test_equals():
    a = Inquiry(resource='books:abc', action='view', context={'ip': '127.0.0.1'})
    b = Inquiry(action='view', resource='books:abc', context={'ip': '127.0.0.1'})
    c = Inquiry(resource='books:абс', action='view', context={'ip': '127.0.0.1'})
    d = Inquiry(resource='books:абс', action='view', context={'ip': '127.0.0.1'})
    assert a == b
    assert b != c
    assert c == d


def test_hash():
    # todo - test more thoroughly
    a = Inquiry(resource='books:abc', action='view', context={'ip': '127.0.0.1'})
    b = Inquiry(action='view', resource='books:abc', context={'ip': '127.0.0.1'})
    c = Inquiry(resource='books:абс', action='view', context={'ip': '127.0.0.1'})
    d = Inquiry(resource='books:абс', action='view', context={'ip': '127.0.0.1'})
    assert hash(a) == hash(b)
    assert hash(b) != hash(c)
    assert hash(c) == hash(d)
