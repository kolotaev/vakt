import pytest

from vakt.rules.string import StartsWith, EndsWith, Contains


def test_substring_rule_classes_constructor_fails():
    expect_msg = 'Initial property should be a string'
    with pytest.raises(TypeError) as excinfo:
        StartsWith(dict())
    assert expect_msg in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        EndsWith(dict())
    assert expect_msg in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        Contains(dict())
    assert expect_msg in str(excinfo.value)


@pytest.mark.parametrize('arg, against, result', [
    ('foo', 'foo', True),
    ('foo', 'Foo', False),
    ('Foo', 'foo', False),
    ('foo', 'bar', False),
    ('foo', 'foobar', True),
    ('foo', 'fo2bar', False),
    ('тест', 'нет', False),
    ('тест', 'тест2', True),
    ('', '', True),
    ('456', ['456'], False),
])
def test_string_starts_with_satisfied(arg, against, result):
    c = StartsWith(arg)
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == StartsWith.from_json(StartsWith(arg).to_json()).satisfied(against)


@pytest.mark.parametrize('arg, against, result', [
    ('foo', 'foo', True),
    ('foo', 'Foo', False),
    ('Foo', 'foo', False),
    ('foo', 'bar', False),
    ('foo', 'barfoo', True),
    ('foo', 'barfo2', False),
    ('тест', 'нет', False),
    ('тест', '2тест', True),
    ('', '', True),
    ('456', 456, False),
])
def test_string_ends_with_satisfied(arg, against, result):
    c = EndsWith(arg)
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == EndsWith.from_json(EndsWith(arg).to_json()).satisfied(against)


@pytest.mark.parametrize('arg, against, result', [
    ('foo', 'foo', True),
    ('foo', 'Foo', False),
    ('Foo', 'foo', False),
    ('foo', 'bar', False),
    ('foo', 'barfoo', True),
    ('foo', 'foobar', True),
    ('foo', 'qwertyfoobar', True),
    ('foo', 'barfo2', False),
    ('тест', 'нет', False),
    ('тест', '2тест7', True),
    ('', '', True),
    ('456', 456, False),
])
def test_string_contains_satisfied(arg, against, result):
    c = Contains(arg)
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == Contains.from_json(Contains(arg).to_json()).satisfied(against)
