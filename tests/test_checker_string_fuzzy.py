import pytest

from vakt.checker import StringFuzzyChecker
from vakt.policy import DefaultPolicy


@pytest.mark.parametrize('policy, field, what, result', [
    (DefaultPolicy('1', actions=['get']), 'actions', 'get', True),
    (DefaultPolicy('1', actions=['get']), 'actions', 'g', True),
    (DefaultPolicy('1', actions=['get']), 'actions', 'et', True),
    (DefaultPolicy('1', actions=['get']), 'actions', 't', True),
    (DefaultPolicy('1', actions=['get', 'list']), 'actions', 'list', True),
    (DefaultPolicy('1', actions=['get', 'list']), 'non_existing_field', 'get', False),
    (DefaultPolicy('1', actions=['<get>']), 'actions', 'get', True),
    (DefaultPolicy('1', actions=['<get>']), 'actions', 'e', True),
    (DefaultPolicy('1', actions=['<get>']), 'actions', '<get>', False),
    (DefaultPolicy('1', actions=['<get>']), 'actions', '<t>', False),
    (DefaultPolicy('1', actions=['<get']), 'actions', 'get', True),
    (DefaultPolicy('1', actions=['<get']), 'actions', 'ge', True),
    (DefaultPolicy('1', resources=['books:1', 'books:2']), 'resources', 'books', True),
    (DefaultPolicy('1', resources=['books:1', 'books:2']), 'resources', ':', True),
    (DefaultPolicy('1', resources=['books:1', 'books:2']), 'resources', '3', False),
])
def test_matches(policy, field, what, result):
    c = StringFuzzyChecker()
    assert result == c.fits(policy, field, what)
