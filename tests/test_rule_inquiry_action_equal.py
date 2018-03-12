import pytest

from vakt.rules.inquiry import ActionEqualRule
from vakt.guard import Inquiry


@pytest.mark.parametrize('what, action, result', [
    ('foo', 'foo', True),
    ('foo', 'bar', False),
    ('тест', 'нет', False),
    ('тест', 'тест', True),
    (1, '1', False),
    ('1', 1, False),
    ('', '', True),
])
def test_action_equal_satisfied(what, action, result):
    i = Inquiry(action=action, resource=None, subject=None)
    c = ActionEqualRule()
    assert result == c.satisfied(what, i)
