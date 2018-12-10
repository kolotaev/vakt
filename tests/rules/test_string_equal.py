import pytest

from vakt.rules.string import StringEqualRule


def test_string_equal_construct_fails():
    with pytest.raises(TypeError) as excinfo:
        StringEqualRule(dict())
    assert 'Initial property should be a string' in str(excinfo.value)


@pytest.mark.parametrize('arg, against, result', [
    ('foo', 'foo', True),
    ('foo', 'bar', False),
    ('тест', 'нет', False),
    ('тест', 'тест', True),
    ('', '', True),
])
def test_string_equal_satisfied(arg, against, result):
    c = StringEqualRule(arg)
    assert result == c.satisfied(against)
