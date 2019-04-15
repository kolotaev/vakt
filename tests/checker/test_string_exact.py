import pytest

from vakt.checker import StringExactChecker
from vakt.policy import Policy
from vakt.rules.operator import Eq


@pytest.mark.parametrize('policy, field, what, result', [
    (Policy('1', actions=['get']), 'actions', 'get', True),
    (Policy('1', actions=['get', 'list']), 'actions', 'get', True),
    (Policy('1', actions=['get', 'list']), 'actions', 'list', True),
    (Policy('1', actions=['get', 'list']), 'non_existing_field', 'get', False),
    (Policy('1', actions=['<get>']), 'actions', 'get', True),
    (Policy('1', actions=['<get>']), 'actions', '<get>', False),
    (Policy('1', actions=['<get']), 'actions', 'get', False),
    (Policy('1', resources=['books:1', 'books:2']), 'resources', 'books:3', False),
    (Policy('1', resources=['books:1', 'books:2']), 'resources', 'books:1', True),
    (Policy('1', actions=[Eq('create')]), 'actions', 'create', False),
    (Policy('1', actions=[{'foo': Eq('create')}]), 'actions', 'create', False),
])
def test_fits(policy, field, what, result):
    c = StringExactChecker()
    assert result == c.fits(policy, field, what)
