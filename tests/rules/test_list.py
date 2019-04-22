import pytest

import vakt.rules.list


def test_initialization():
    with pytest.raises(TypeError) as excinfo:
        vakt.rules.list.In([1, 5], [1, 9])
    assert 'unhashable' in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        vakt.rules.list.In({'a': 90}, {'v': "value"})
    assert 'unhashable' in str(excinfo.value)


# In List
@pytest.mark.parametrize('data, what, result', [
    ([], 1, False),
    ([1, 45, 78], 1, True),
    ([1, 45, 78], 5, False),
    ([8789.45, 908.8989, 34545.2], 1.0, False),
    ([''], '', True),
    (['a', 'b'], 'a', True),
    (['a', 'b'], 'c', False),
])
def test_in_list(data, what, result):
    c = vakt.rules.list.In(*data)
    assert result == c.satisfied(what)
    # test after (de)serialization
    jsn = vakt.rules.list.In(*data).to_json()
    c1 = vakt.rules.list.In.from_json(jsn)
    assert result == c1.satisfied(what)


# Not In List
@pytest.mark.parametrize('data, what, result', [
    ([], 1, True),
    ([1, 45, 78], 1, False),
    ([1, 45, 78], 5, True),
    ([8789.45, 908.8989, 34545.2], 1.0, True),
    ([''], '', False),
    (['a', 'b'], 'a', False),
    (['a', 'b'], 'c', True),
])
def test_not_in_list(data, what, result):
    c = vakt.rules.list.NotIn(*data)
    assert result == c.satisfied(what)
    # test after (de)serialization
    jsn = vakt.rules.list.NotIn(*data).to_json()
    c1 = vakt.rules.list.NotIn.from_json(jsn)
    assert result == c1.satisfied(what)


# All In List
@pytest.mark.parametrize('data, what, result', [
    ([], [], True),
    ([1, 3, 5, 90], [1, 3, 5, 90], True),
    ([1, 3, 5, 90], [1, 90, 3, 5], True),
    ([1, 3.0, 5.0, 90], [1, 90, 3, 5], True),
    ([1, 3.0, 5.1, 90], [1, 90, 3, 5], False),
    (['a', 'f', 'g'], ['a', 'f'], True),
    (['a', 'f', 'g'], ['f', 'a'], True),
    (['f', 'a', 'y'], ['f', 'a', 'y', 'u'], False),
])
def test_all_in_list(data, what, result):
    c = vakt.rules.list.AllIn(*data)
    assert result == c.satisfied(what)
    # test after (de)serialization
    jsn = vakt.rules.list.AllIn(*data).to_json()
    c1 = vakt.rules.list.AllIn.from_json(jsn)
    assert result == c1.satisfied(what)


@pytest.mark.parametrize('val', [
    1,
    '',
    's',
    {},
    {'a': 90},
])
def test_all_in_list_satisfied_wrong_arg(val):
    rule = vakt.rules.list.AllIn('io', 'util')
    with pytest.raises(TypeError) as excinfo:
        rule.satisfied(val)
    assert 'Value should be of list type' == str(excinfo.value)


# All Not In List
@pytest.mark.parametrize('data, what, result', [
    ([], [], False),
    ([], [1], True),
    ([], [1, 3], True),
    ([1, 3, 5, 90], [1, 3, 5, 90], False),
    ([1, 3, 5, 90], [1, 90, 3, 5], False),
    ([1, 3.0, 5.0, 90], [1, 90, 3, 5], False),
    ([1, 3.0, 5.0, 90], [2], True),
    ([1, 3.0, 5.0, 90], [2, 8], True),
    ([1, 3.0, 5.0, 90], [8, 2, 8], True),
    ([1, 3.0, 5.0, 90], [5, 2, 8], True),
    (['a', 'f', 'g'], ['a', 'f'], False),
    (['a', 'f', 'g'], ['f', 'a'], False),
    (['a', 'f', 'g'], ['x', 'u'], True),
    (['f', 'a', 'y'], ['f', 'a', 'y', 'u'], True),
])
def test_all_not_in_list(data, what, result):
    c = vakt.rules.list.AllNotIn(*data)
    assert result == c.satisfied(what)
    # test after (de)serialization
    jsn = vakt.rules.list.AllNotIn(*data).to_json()
    c1 = vakt.rules.list.AllNotIn.from_json(jsn)
    assert result == c1.satisfied(what)


@pytest.mark.parametrize('val', [
    1,
    '',
    's',
    {},
    {'a': 90},
])
def test_all_not_in_list_satisfied_wrong_arg(val):
    rule = vakt.rules.list.AllNotIn(*[])
    with pytest.raises(TypeError) as excinfo:
        rule.satisfied(val)
    assert 'Value should be of list type' == str(excinfo.value)


# Any In List
@pytest.mark.parametrize('data, what, result', [
    ([], [], False),
    ([], [1], False),
    ([], [1, 4], False),
    ([1, 3, 5, 90], [1, 3, 5, 90], True),
    ([1, 3, 5, 90], [1, 90, 3, 5], True),
    ([1, 3.0, 5.0, 90], [1, 90, 3, 5], True),
    ([1, 3.0, 5.0, 90], [2], False),
    ([1, 3.0, 5.0, 90], [2, 8], False),
    ([1, 3.0, 5.0, 90], [8, 2, 8], False),
    ([1, 3.0, 5.0, 90], [5, 2, 8], True),
    ([1, 3.0, 5.01, 90], [5, 2, 8], False),
    ([1, 3.0, 5.7, 90], [2, 8, 5.7], True),
    (['a', 'f', 'g'], ['a', 'f'], True),
    (['a', 'f', 'g'], ['c', 'g', 'o'], True),
    (['a', 'f', 'g'], ['x', 'u'], False),
    (['f', 'a', 'y'], ['f', 'a', 'y', 'u'], True),
])
def test_any_in_list(data, what, result):
    c = vakt.rules.list.AnyIn(*data)
    assert result == c.satisfied(what)
    # test after (de)serialization
    jsn = vakt.rules.list.AnyIn(*data).to_json()
    c1 = vakt.rules.list.AnyIn.from_json(jsn)
    assert result == c1.satisfied(what)


@pytest.mark.parametrize('val', [
    1,
    '',
    's',
    {},
    {'a': 90},
])
def test_any_in_list_satisfied_wrong_arg(val):
    rule = vakt.rules.list.AnyIn('oop')
    with pytest.raises(TypeError) as excinfo:
        rule.satisfied(val)
    assert 'Value should be of list type' == str(excinfo.value)


# Any Not In List
@pytest.mark.parametrize('data, what, result', [
    ([], [], False),
    ([], [1], True),
    ([], [1, 4], True),
    ([1, 2], [1, 4], True),
    ([1, 2], [1, 2], False),
    ([1, 3, 5, 90], [1, 3, 5, 90], False),
    ([1, 3, 5, 90], [1, 90, 3, 5], False),
    ([1, 3.0, 5.0, 90], [1, 90, 3, 5], False),
    ([1, 3.0, 5.0, 90], [2], True),
    ([1, 3.0, 5.0, 90], [2, 3.0], True),
    ([1, 3.0, 5.0, 90], [2, 8], True),
    ([1, 3.0, 5.0, 90], [8, 2, 8], True),
    ([1, 3.0, 5.0, 90], [5, 2, 8], True),
    ([1, 3.0, 5.7, 90], [2, 8, 5.7], True),
    (['a', 'f', 'g'], ['a', 'f'], False),
    (['a', 'f', 'g'], ['a', 'f', 'p'], True),
    (['a', 'f', 'g'], ['c', 'g', 'o'], True),
    (['a', 'f', 'g'], ['a', 'f', 'g'], False),
    (['a', 'f', 'g'], ['a', 'g', 'f'], False),
    (['a', 'f', 'g'], ['x', 'u'], True),
    (['f', 'a', 'y'], ['f', 'a', 'y', 'u'], True),
])
def test_any_not_in_list(data, what, result):
    c = vakt.rules.list.AnyNotIn(*data)
    assert result == c.satisfied(what)
    # test after (de)serialization
    jsn = vakt.rules.list.AnyNotIn(*data).to_json()
    c1 = vakt.rules.list.AnyNotIn.from_json(jsn)
    assert result == c1.satisfied(what)


@pytest.mark.parametrize('val', [
    1,
    '',
    's',
    {},
    {'a': 90},
])
def test_any_not_in_list_satisfied_wrong_arg(val):
    rule = vakt.rules.list.AnyNotIn('xyz')
    with pytest.raises(TypeError) as excinfo:
        rule.satisfied(val)
    assert 'Value should be of list type' == str(excinfo.value)
