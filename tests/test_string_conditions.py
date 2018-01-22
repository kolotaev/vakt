import pytest

from vakt.conditions.string import StringEqualCondition, StringPairsEqualCondition


def test_string_equal_construct_fails():
    with pytest.raises(TypeError) as excinfo:
        StringEqualCondition(dict())
    assert 'equals property should be a string' in str(excinfo.value)


@pytest.mark.parametrize('arg, against, result', [
    ('foo', 'foo', True),
    ('foo', 'bar', False),
    ('тест', 'нет', False),
    ('тест', 'тест', True),
    ('', '', True),
])
def test_string_equal_satisfied(arg, against, result):
    c = StringEqualCondition(arg)
    assert result == c.satisfied(against)
