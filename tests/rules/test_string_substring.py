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


@pytest.mark.parametrize('arg, against, case_insensitive, result', [
    ('foo', 'foo', False, True),
    ('foo', 'Foo', False, False),
    ('foo', 'Foo', True, True),
    ('Foo', 'foo', False, False),
    ('foo', 'bar', False, False),
    ('foo', 'foobar', False, True),
    ('foo', 'fooBar', True, True),
    ('foo', 'fo2bar', False, False),
    ('foo', 'fo2Bar', True, False),
    ('тест', 'нет', False, False),
    ('тест', 'Hет', True, False),
    ('тест', 'тест2', False, True),
    ('тест', 'тЕст2', True, True),
    ('', '', False, True),
    ('456', ['456'], False, False),
    ('456', ['456'], True, False),
])
def test_string_starts_with_satisfied(arg, against, case_insensitive, result):
    c = StartsWith(arg, ci=case_insensitive)
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == StartsWith.from_json(StartsWith(arg, ci=case_insensitive).to_json()).satisfied(against)


@pytest.mark.parametrize('arg, against, case_insensitive, result', [
    ('foo', 'foo', False, True),
    ('foo', 'foo', True, True),
    ('foo', 'Foo', False, False),
    ('foo', 'Foo', True, True),
    ('Foo', 'foo', False, False),
    ('foo', 'bar', False, False),
    ('foo', 'barfoo', False, True),
    ('foo', 'barFoo', True, True),
    ('foo', 'barfo2', False, False),
    ('foo', 'barfo2', True, False),
    ('тест', 'нет', False, False),
    ('тест', 'Нет', True, False),
    ('тест', '2тест', False, True),
    ('тест', '2тЕст', True, True),
    ('', '', False, True),
    ('', '', True, True),
    ('456', 456, False, False),
    ('456', 456, True, False),
])
def test_string_ends_with_satisfied(arg, against, case_insensitive, result):
    c = EndsWith(arg, ci=case_insensitive)
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == EndsWith.from_json(EndsWith(arg, ci=case_insensitive).to_json()).satisfied(against)


@pytest.mark.parametrize('arg, against, case_insensitive, result', [
    ('foo', 'foo', False, True),
    ('foo', 'foo', True, True),
    ('foo', 'Foo', False, False),
    ('foo', 'Foo', True, True),
    ('Foo', 'foo', False, False),
    ('Foo', 'foo', True, True),
    ('foo', 'bar', False, False),
    ('foo', 'bar', True, False),
    ('foo', 'barfoo', False, True),
    ('foo', 'barFoo', True, True),
    ('foo', 'foobar', False, True),
    ('foo', 'fooBar', True, True),
    ('foo', 'qwertyfoobar', False, True),
    ('foo', 'qwerTYfoobar', True, True),
    ('foo', 'barfo2', False, False),
    ('foo', 'bARFo2', True, False),
    ('тест', 'нет', False, False),
    ('тест', 'нет', True, False),
    ('тест', '2тест7', False, True),
    ('тест', '2теСТ7', True, True),
    ('', '', False, True),
    ('', '', True, True),
    ('456', 456, False, False),
    ('456', 456, True, False),
])
def test_string_contains_satisfied(arg, against, case_insensitive, result):
    c = Contains(arg, ci=case_insensitive)
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == Contains.from_json(Contains(arg, ci=case_insensitive).to_json()).satisfied(against)
