import pytest

from vakt.rules.inquiry import ResourceInRule
from vakt.guard import Inquiry


@pytest.mark.parametrize('what, resource, result', [
    (['foo'], 'foo', True),
    (['foo', 'bar'], 'foo', True),
    (['foo bar'], 'foo', False),
    ([], 'foo', False),
    ('', 'foo', False),
    ({}, 'foo', False),
    (None, 'foo', False),
])
def test_string_equal_satisfied(what, resource, result):
    i = Inquiry(action='get', resource=resource, subject='Max')
    c = ResourceInRule()
    assert result == c.satisfied(what, i)
