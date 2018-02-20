import pytest

from vakt.guard import Request


def test_json_roundtrip():
    r = Request(resource='books:abc', action='view', subject='bobby', context={'ip': '127.0.0.1'})
    s = r.to_json()
    r1 = Request.from_json(s)
    assert 'books:abc' == r1.resource
    assert 'view' == r1.action
    assert 'bobby' == r1.subject
    assert {'ip': '127.0.0.1'} == r1.context


def test_json_decode_fails_for_incorrect_data():
    with pytest.raises(ValueError):
        Request.from_json('{')


def test_can_create_empty_request():
    r = Request()
    assert isinstance(r, Request)
    r2 = Request.from_json('{}')
    assert isinstance(r2, Request)


def test_pretty_print():
    r = Request(resource='books:abc', action='view', context={'ip': '127.0.0.1'})
    assert "<class 'vakt.guard.Request'>: {'resource': 'books:abc', 'action': 'view', " + \
           "'subject': None, 'context': {'ip': '127.0.0.1'}}" == str(r)
