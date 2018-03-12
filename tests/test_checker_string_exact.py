import pytest

from vakt.checker import StringExactChecker
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
    c = StringExactChecker()
    assert result == c.fits(policy, field, what)
