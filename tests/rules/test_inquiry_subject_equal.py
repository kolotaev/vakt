import pytest

from vakt.rules.inquiry import SubjectEqual, SubjectEqualRule
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
    c = SubjectEqual()
    assert result == c.satisfied(what, i)
    # test after (de)serialization
    jsn = SubjectEqual().to_json()
    c1 = SubjectEqual.from_json(jsn)
    assert result == c1.satisfied(what, i)
    # test deprecated class
    with pytest.deprecated_call():
        i = Inquiry(action='get', resource=None, subject=subject)
        c = SubjectEqualRule()
        assert result == c.satisfied(what, i)
        assert result == SubjectEqualRule.from_json(c.to_json()).satisfied(what, i)
