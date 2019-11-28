import pytest

from vakt.rules.inquiry import ResourceIn
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
def test_resource_in_satisfied(what, resource, result):
    i = Inquiry(action='get', resource=resource, subject='Max')
    c = ResourceIn()
    assert result == c.satisfied(what, i)
    # test after (de)serialization
    jsn = ResourceIn().to_json()
    c1 = ResourceIn.from_json(jsn)
    assert result == c1.satisfied(what, i)
