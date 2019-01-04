import pytest

from vakt.rules.string import Equal, StringEqualRule, EqualInsensitive


def test_string_equal_construct_fails():
    with pytest.raises(TypeError) as excinfo:
        StringEqualRule(dict())
    assert 'Initial property should be a string' in str(excinfo.value)


@pytest.mark.parametrize('arg, against, result', [
    ('foo', 'foo', True),
    ('foo', 'Foo', False),
    ('Foo', 'foo', False),
    ('foo', 'bar', False),
    ('тест', 'нет', False),
    ('тест', 'тест', True),
    ('тест', 'тЕст', False),
    ('', '', True),
])
def test_string_equal_satisfied(arg, against, result):
    c = Equal(arg)
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == Equal.from_json(Equal(arg).to_json()).satisfied(against)
    # test deprecated class
    c = StringEqualRule(arg)
    assert result == c.satisfied(against)


def test_string_equal_insensitive_construct_fails():
    with pytest.raises(TypeError) as excinfo:
        EqualInsensitive(123456)
    assert 'Initial property should be a string' in str(excinfo.value)


@pytest.mark.parametrize('arg, against, result', [
    ('foo', 'foo', True),
    ('foo', 'Foo', True),
    ('Foo', 'foo', True),
    ('foo', 'bar', False),
    ('foo', 'Bar', False),
    ('тест', 'нет', False),
    ('тест', 'тест', True),
    ('тест', 'тЕст', True),
    ('', '', True),
])
def test_string_equal_insensitive_satisfied(arg, against, result):
    c = EqualInsensitive(arg)
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == EqualInsensitive.from_json(EqualInsensitive(arg).to_json()).satisfied(against)
