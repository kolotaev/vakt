import pytest

from vakt.checker import RegexChecker
from vakt.policy import Policy
from vakt.rules.operator import Eq


@pytest.mark.parametrize('policy, field, what, result', [
    (Policy('1', actions=['get']), 'actions', 'get', True),
    (Policy('1', actions=['get']), 'actions', 'GET', False),
    (Policy('1', actions=['<.*>']), 'actions', '', True),
    (Policy('1', actions=[r'<get[\d]{5}>']), 'actions', 'get12345', True),
    (Policy('1', actions=[r'<get[\d]{5}>']), 'actions', 'get1234', False),
    (Policy('1', actions=['get', r'<list[\d]{3}>']), 'actions', 'list123', True),
    (Policy('1', actions=['get', r'list[\d]{3}']), 'actions', 'list123', False),
    (Policy('1', actions=['get', 'list']), 'non_existing_field', 'get', False),
    (Policy('1', actions=['<get>']), 'actions', 'get', True),
    (Policy('1', actions=['<get>']), 'actions', 'GET', False),
    (Policy('1', actions=['<getty>']), 'actions', 'get', False),
    (Policy('1', actions=['<get']), 'actions', 'get', False),
    (Policy('1', resources=[r'<[\d]{1}>', r'<[\d]{2}>']), 'resources', 'y', False),
    (Policy('1', resources=[r'<[\d]{1}>', r'<[\d]{2}>']), 'resources', '12', True),
    (Policy('1', actions=['get', 'delete']), 'actions', 'create', False),
    (Policy('1', actions=[Eq('create')]), 'actions', 'create', False),
    (Policy('1', actions=[{'foo': Eq('create')}]), 'actions', 'create', False),
])
def test_fits(policy, field, what, result):
    c = RegexChecker()
    assert result == c.fits(policy, field, what)
