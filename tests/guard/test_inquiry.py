import pytest

from vakt.guard import Inquiry


def test_default_values():
    i = Inquiry()
    assert '' == i.subject
    assert '' == i.action
    assert '' == i.resource
    assert {} == i.context
    assert 1 == i.type


@pytest.mark.parametrize('resource, action, subject, context, type', [
    ('', '', '', None, 1),
    ('a', 'b', 'c', None, 1),
    ('a', 'b', 'c', {'x': 'y'}, 1),
    ({'a': 'b'}, None, None, None, 2),
    ({'a': 'b'}, {'aa': 'bb'}, {'aaa': 'bbb'}, {'x': 'y'}, 2),
])
def test_creation_based_on_type(resource, action, subject, context, type):
    i = Inquiry(resource=resource, action=action, subject=subject, context=context)
    assert type == i.type


def test_json_roundtrip():
    i = Inquiry(resource='books:abc', action='view', subject='bobby', context={'ip': '127.0.0.1'})
    s = i.to_json()
    r1 = Inquiry.from_json(s)
    assert 'books:abc' == r1.resource
    assert 'view' == r1.action
    assert 'bobby' == r1.subject
    assert {'ip': '127.0.0.1'} == r1.context
    assert 1 == r1.type


def test_from_json_skips_type():
    s = '{"resource": {"a": "b"}, "action": {"x": "y"}, "subject": {"c": "d"}, "context": {}, "type": 1}'
    i = Inquiry.from_json(s)
    assert 2 == i.type


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
