import pytest

from vakt.matcher import StringExactMatcher
from vakt.policy import DefaultPolicy


@pytest.mark.parametrize('policy, field, what, result', [
    (DefaultPolicy('1', actions=['get']), 'actions', 'get', True),
    (DefaultPolicy('1', actions=['get', 'list']), 'actions', 'get', True),
    (DefaultPolicy('1', actions=['get', 'list']), 'actions', 'list', True),
    (DefaultPolicy('1', actions=['get', 'list']), 'non_existing_field', 'get', False),
    (DefaultPolicy('1', actions=['<get>']), 'actions', 'get', True),
    (DefaultPolicy('1', actions=['<get>']), 'actions', '<get>', False),
    (DefaultPolicy('1', actions=['<get']), 'actions', 'get', False),
    (DefaultPolicy('1', resources=['books:1', 'books:2']), 'resources', 'books:3', False),
    (DefaultPolicy('1', resources=['books:1', 'books:2']), 'resources', 'books:1', True),
])
def test_matches(policy, field, what, result):
    m = StringExactMatcher()
    assert result == m.matches(policy, field, what)
