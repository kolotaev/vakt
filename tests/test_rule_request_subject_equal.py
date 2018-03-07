import pytest

from vakt.rules.request import SubjectEqualRule
from vakt.guard import Request


@pytest.mark.parametrize('what, subject, result', [
    ('foo', 'foo', True),
    ('foo', 'bar', False),
    ('тест', 'нет', False),
    ('тест', 'тест', True),
    (1, '1', False),
    ('1', 1, False),
    ('', '', True),
])
def test_string_equal_satisfied(what, subject, result):
    r = Request(action='get', resource=None, subject=subject)
    c = SubjectEqualRule()
    assert result == c.satisfied(what, r)
