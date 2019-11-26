import pytest

from vakt.rules.inquiry import ActionMatch, ResourceMatch, SubjectMatch
from vakt.guard import Inquiry


@pytest.mark.parametrize('attribute, what, inquiry, result', [
    # no inquiry passed
    ('foo', 'bar', None, False),
    ('foo', 'foo', None, False),
    # matching on not attribute
    (None, 'get', Inquiry(action='get', resource='fax', subject='Max'), True),
    (None, 'put', Inquiry(action='get', resource='fax', subject='Max'), False),
    (None, 'getty', Inquiry(action='get', resource='fax', subject='Max'), False),
    (None, 'iget', Inquiry(action='get', resource='fax', subject='Max'), False),
    (None, 9999, Inquiry(action=9999, resource='fax', subject='Max'), True),
    (None, 8888, Inquiry(action=9999, resource='fax', subject='Max'), False),
    # matching on attribute
    ('user_id', 'get', Inquiry(action='get', resource='fax', subject='Max'), False),
    ('user_id', '123', Inquiry(action='get', resource='fax', subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', 'get', Inquiry(action='get', resource='fax', subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', '123', Inquiry(action={'resource': 'book', 'user_id': '123'},
                               resource='fax',
                               subject={'name': 'Max', 'user_id': '123'}), True),
    ('user_id', '123', Inquiry(action={'resource': 'book'},
                               resource='fax',
                               subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', '456', Inquiry(action={'resource': 'book', 'user_id': '123'},
                               resource='fax',
                               subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', 123, Inquiry(action={'resource': 'book', 'user_id': 123},
                             resource='fax',
                             subject={'name': 'Max'}), True),
    ('user_id', 456, Inquiry(action={'resource': 'book', 'user_id': 123},
                             resource='fax',
                             subject={'name': 'Max'}), False),
    ('user_id', 123, Inquiry(action={'resource': 'book', 'user_id': '123'},
                             resource='fax',
                             subject={'name': 'Max'}), False),
])
def test_action_match_satisfied(attribute, what, inquiry, result):
    c = ActionMatch(attribute)
    assert result == c.satisfied(what, inquiry)
    # test after (de)serialization
    jsn = ActionMatch(attribute).to_json()
    c1 = ActionMatch.from_json(jsn)
    assert result == c1.satisfied(what, inquiry)


@pytest.mark.parametrize('attribute, what, inquiry, result', [
    # no inquiry passed
    ('foo', 'bar', None, False),
    ('foo', 'foo', None, False),
    # matching on not attribute
    (None, 'Max', Inquiry(action='get', resource='fax', subject='Max'), True),
    (None, 'Peter', Inquiry(action='get', resource='fax', subject='Max'), False),
    (None, 'Maxy', Inquiry(action='get', resource='fax', subject='Max'), False),
    (None, 'IMax', Inquiry(action='get', resource='fax', subject='Max'), False),
    (None, 9999, Inquiry(action='get', resource='fax', subject=9999), True),
    (None, 8888, Inquiry(action='get', resource='fax', subject=9999), False),
    # matching on attribute
    ('user_id', 'Max', Inquiry(action='get', resource='fax', subject='Max'), False),
    ('user_id', 'Max', Inquiry(action={'name': 'get', 'user_id': '123'}, resource='fax', subject='Max'), False),
    ('user_id', 'Jack', Inquiry(action={'name': 'get', 'user_id': '123'}, resource='fax', subject='Max'), False),
    ('user_id', '123', Inquiry(action={'resource': 'book', 'user_id': '123'},
                               resource='fax',
                               subject={'name': 'Max', 'user_id': '123'}), True),
    ('user_id', '123', Inquiry(action={'resource': 'book', 'user_id': '123'},
                               resource='fax',
                               subject={'name': 'Max'}), False),
    ('user_id', '456', Inquiry(action={'resource': 'book', 'user_id': '123'},
                               resource='fax',
                               subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', 123, Inquiry(action={'resource': 'book'},
                             resource='fax',
                             subject={'name': 'Max', 'user_id': 123}), True),
    ('user_id', 456, Inquiry(action={'resource': 'book'},
                             resource='fax',
                             subject={'name': 'Max', 'user_id': 123}), False),
    ('user_id', 123, Inquiry(action={'resource': 'book'},
                             resource='fax',
                             subject={'name': 'Max', 'user_id': '123'}), False),
])
def test_subject_match_satisfied(attribute, what, inquiry, result):
    c = SubjectMatch(attribute)
    assert result == c.satisfied(what, inquiry)
    # test after (de)serialization
    jsn = SubjectMatch(attribute).to_json()
    c1 = SubjectMatch.from_json(jsn)
    assert result == c1.satisfied(what, inquiry)


@pytest.mark.parametrize('attribute, what, inquiry, result', [
    # no inquiry passed
    ('foo', 'bar', None, False),
    ('foo', 'foo', None, False),
    # matching on not attribute
    (None, 'fax', Inquiry(action='get', resource='fax', subject='Max'), True),
    (None, 'phone', Inquiry(action='get', resource='fax', subject='Max'), False),
    (None, 'Fax', Inquiry(action='get', resource='fax', subject='Max'), False),
    (None, 'my-fax-1', Inquiry(action='get', resource='fax', subject='Max'), False),
    (None, 9999, Inquiry(action='get', resource=9999, subject='Max'), True),
    (None, 8888, Inquiry(action='get', resource=9999, subject='Max'), False),
    # matching on attribute
    ('user_id', 'fax', Inquiry(action='get', resource='fax', subject='Max'), False),
    ('user_id', 'fax', Inquiry(action='get', resource='fax', subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', 'phone', Inquiry(action='get', resource='fax', subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', '123', Inquiry(action='get',
                               resource={'name': 'book', 'user_id': '123'},
                               subject={'name': 'Max', 'user_id': '123'}), True),
    ('user_id', '123', Inquiry(action='get',
                               resource={'name': 'book'},
                               subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', '456', Inquiry(action='get',
                               resource={'name': 'book', 'user_id': '123'},
                               subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', 123, Inquiry(action='get',
                             resource={'name': 'book', 'user_id': 123},
                             subject={'name': 'Max', 'user_id': '123'}), True),
    ('user_id', 456, Inquiry(action='get',
                             resource={'name': 'book', 'user_id': 123},
                             subject={'name': 'Max', 'user_id': '123'}), False),
    ('user_id', 123, Inquiry(action='get',
                             resource={'name': 'book', 'user_id': '123'},
                             subject={'name': 'Max', 'user_id': '123'}), False),
])
def test_resource_match_satisfied(attribute, what, inquiry, result):
    c = ResourceMatch(attribute)
    assert result == c.satisfied(what, inquiry)
    # test after (de)serialization
    jsn = ResourceMatch(attribute).to_json()
    c1 = ResourceMatch.from_json(jsn)
    assert result == c1.satisfied(what, inquiry)
