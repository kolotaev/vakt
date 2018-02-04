import pytest

from vakt.matcher import RegexMatcher
from vakt.policy import DefaultPolicy


@pytest.mark.parametrize('policy, field, what, result', [
    (DefaultPolicy('1', actions=['get']), 'actions', 'get', True),
    (DefaultPolicy('1', actions=['<.*>']), 'actions', '', True),
    (DefaultPolicy('1', actions=['<get[\d]{5}>']), 'actions', 'get12345', True),
    (DefaultPolicy('1', actions=['<get[\d]{5}>']), 'actions', 'get1234', False),
    (DefaultPolicy('1', actions=['get', '<list[\d]{3}>']), 'actions', 'list123', True),
    (DefaultPolicy('1', actions=['get', 'list[\d]{3}']), 'actions', 'list123', False),
    (DefaultPolicy('1', actions=['get', 'list']), 'non_existing_field', 'get', False),
    (DefaultPolicy('1', actions=['<get>']), 'actions', 'get', True),
    (DefaultPolicy('1', actions=['<getty>']), 'actions', 'get', False),
    (DefaultPolicy('1', actions=['<get']), 'actions', 'get', False),
    (DefaultPolicy('1', resources=['<[\d]{1}>', '<[\d]{2}>']), 'resources', 'y', False),
    (DefaultPolicy('1', resources=['<[\d]{1}>', '<[\d]{2}>']), 'resources', '12', True),
])
def test_matches(policy, field, what, result):
    m = RegexMatcher()
    assert result == m.matches(policy, field, what)
