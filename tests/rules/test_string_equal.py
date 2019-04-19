import pytest

from vakt.rules.string import Equal, StringEqualRule


def test_string_equal_constructor_fails():
    with pytest.raises(TypeError) as excinfo:
        Equal(dict())
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
    with pytest.deprecated_call():
        c = StringEqualRule(arg)
        assert result == c.satisfied(against)


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
    c = Equal(arg, ci=True)
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == Equal.from_json(c.to_json()).satisfied(against)
