import pytest

from vakt.checker import RegexChecker
from vakt.policy import Policy


@pytest.mark.parametrize('policy, field, what, result', [
    (Policy('1', actions=['get']), 'actions', 'get', True),
    (Policy('1', actions=['<.*>']), 'actions', '', True),
    (Policy('1', actions=['<get[\d]{5}>']), 'actions', 'get12345', True),
    (Policy('1', actions=['<get[\d]{5}>']), 'actions', 'get1234', False),
    (Policy('1', actions=['get', '<list[\d]{3}>']), 'actions', 'list123', True),
    (Policy('1', actions=['get', 'list[\d]{3}']), 'actions', 'list123', False),
    (Policy('1', actions=['get', 'list']), 'non_existing_field', 'get', False),
    (Policy('1', actions=['<get>']), 'actions', 'get', True),
    (Policy('1', actions=['<getty>']), 'actions', 'get', False),
    (Policy('1', actions=['<get']), 'actions', 'get', False),
    (Policy('1', resources=['<[\d]{1}>', '<[\d]{2}>']), 'resources', 'y', False),
    (Policy('1', resources=['<[\d]{1}>', '<[\d]{2}>']), 'resources', '12', True),
])
def test_matches(policy, field, what, result):
    c = RegexChecker()
    assert result == c.fits(policy, field, what)
