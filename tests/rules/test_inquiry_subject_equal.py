import pytest

from vakt.rules.inquiry import SubjectEqualRule
from vakt.guard import Inquiry


@pytest.mark.parametrize('what, subject, result', [
    ('foo', 'foo', True),
    ('foo', 'bar', False),
    ('тест', 'нет', False),
    ('тест', 'тест', True),
    (1, '1', False),
    ('1', 1, False),
    ('', '', True),
])
def test_subject_equal_satisfied(what, subject, result):
    i = Inquiry(action='get', resource=None, subject=subject)
    c = SubjectEqualRule()
    assert result == c.satisfied(what, i)
