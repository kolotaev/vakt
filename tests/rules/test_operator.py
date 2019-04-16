from datetime import datetime as dt

import pytest

from vakt.rules.operator import *
from vakt.rules.base import Rule


class A:
    def __init__(self, a):
        self.a = a


class B(A):
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


@pytest.mark.parametrize('val, against, result', [
    ('', '', True),
    ('foo', 'foo', True),
    ('foo', 'fo0', False),
    ('русский', 'русский', True),
    ('русский', 'нет', False),
    (1, 1, True),
    (1.0, 1.0, True),
    (-1.0000008, -1.0000008, True),
    (50, 50.1, False),
    (50, 50.0, True),
    ('1', '1', True),
    ('1', 1, False),
    ((), (), False),
    ((1, 2), (1, 2), False),
    (['1', '2'], ['1', '2'], True),
    (['1', '2'], ['2', '1'], False),
    (['1', '2'], ['1', '3'], False),
    ({}, {}, True),
    ({'a': [1, 2]}, {'a': [1, 2]}, True),
    ({'a': [1, 2]}, {'a': [2, 1]}, False),
    ({'a': [1, 2]}, {'a': [1, 3]}, False),
    (A(1), A(1), False),
    (B(1), B(1), True),
    (A(1), A(2), False),
    (B(1), B(2), False),
    (dt.strptime("2018-01-21 02:37:21", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:21", "%Y-%m-%d %H:%M:%S"), True),
    (dt.strptime("2018-01-21 02:37:21", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:55", "%Y-%m-%d %H:%M:%S"), False),
])
def test_eq_satisfied(val, against, result):
    c = Eq(val)
    assert result == c.satisfied(against)
    # test after (de)serialization
    jsn = Eq(val).to_json()
    c1 = Rule.from_json(jsn)
    assert result == c1.satisfied(against)


@pytest.mark.parametrize('val, against, result', [
    ('', '', False),
    ('foo', 'foo', False),
    ('foo', 'fo0', True),
    ('русский', 'русский', False),
    ('русский', 'нет', True),
    (1, 1, False),
    (1.0, 1.0, False),
    (-1.0000008, -1.0000008, False),
    (50, 50.1, True),
    (50, 50.0, False),
    ('1', '1', False),
    ('1', 1, True),
    ((), (), True),
    ((1, 2), (1, 2), True),
    (['1', '2'], ['1', '2'], False),
    (['1', '2'], ['2', '1'], True),
    (['1', '2'], ['1', '3'], True),
    ({}, {}, False),
    ({'a': [1, 2]}, {'a': [1, 2]}, False),
    ({'a': [1, 2]}, {'a': [2, 1]}, True),
    ({'a': [1, 2]}, {'a': [1, 3]}, True),
    (A(1), A(1), True),
    (B(1), B(1), False),
    (A(1), A(2), True),
    (B(1), B(2), True),
    (dt.strptime("2018-01-21 02:37:21", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:21", "%Y-%m-%d %H:%M:%S"), False),
    (dt.strptime("2018-01-21 02:37:21", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:55", "%Y-%m-%d %H:%M:%S"), True),
])
def test_not_eq_satisfied(val, against, result):
    c = NotEq(val)
    assert result == c.satisfied(against)
    # test after (de)serialization
    jsn = NotEq(val).to_json()
    c1 = Rule.from_json(jsn)
    assert result == c1.satisfied(against)


@pytest.mark.parametrize('val, against, result', [
    ('', '', False),
    ('foo', 'foo', False),
    ('foo', 'fo0', False),
    ('русский', 'русский', False),
    ('русский', 'нет', False),
    ('один', 'один-два', True),
    (1, 1, False),
    (1, 10, True),
    (-30, -20, True),
    (1.0, 1.0, False),
    (1.0, 1.0001, True),
    (1.0001, 1.0, False),
    (50, 50.1, True),
    (50, 50.0, False),
    ('1', '1', False),
    ('1', '3', True),
    ('3', '1', False),
    ((), (), False),
    ((1, 2), (1, 2), False),
    ((1, 2), (1, 2, 3), True),
    ((1, 2, 3), (1, 2), False),
    (['1', '2'], ['1', '2'], False),
    (['1', '2'], ['1', '2', '3'], True),
    ([1, 2], [1, 2, 3], True),
    ([1, 2, 3], [1, 2], False),
    (['1', '2'], ['2', '1'], True),
    (['1', '2'], ['1', '3'], True),
    (['2', '1'], ['1', '2'], False),
    (dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"), False),
    (dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:59", "%Y-%m-%d %H:%M:%S"), True),
    (dt.strptime("2018-01-21 02:37:59", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"), False),
])
def test_greater_satisfied(val, against, result):
    c = Greater(val)
    assert result == c.satisfied(against)
    # test after (de)serialization
    jsn = Greater(val).to_json()
    c1 = Rule.from_json(jsn)
    assert result == c1.satisfied(against)


@pytest.mark.parametrize('val, against, result', [
    ('', '', False),
    ('foo', 'foo', False),
    ('foo', 'fo0', True),
    ('русский', 'русский', False),
    ('русский', 'нет', True),
    ('один', 'один-два', False),
    (1, 1, False),
    (1, 10, False),
    (-30, -20, False),
    (1.0, 1.0, False),
    (1.0, 1.0001, False),
    (1.0001, 1.0, True),
    (50, 50.1, False),
    (50, 50.0, False),
    ('1', '1', False),
    ('1', '3', False),
    ('3', '1', True),
    ((), (), False),
    ((1, 2), (1, 2), False),
    ((1, 2), (1, 2, 3), False),
    ((1, 2, 3), (1, 2), True),
    (['1', '2'], ['1', '2'], False),
    (['1', '2'], ['1', '2', '3'], False),
    ([1, 2], [1, 2, 3], False),
    ([1, 2, 3], [1, 2], True),
    (['1', '2'], ['2', '1'], False),
    (['1', '2'], ['1', '3'], False),
    (['2', '1'], ['1', '2'], True),
    (dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"), False),
    (dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:59", "%Y-%m-%d %H:%M:%S"), False),
    (dt.strptime("2018-01-21 02:37:59", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"), True),
])
def test_less_satisfied(val, against, result):
    c = Less(val)
    assert result == c.satisfied(against)
    # test after (de)serialization
    jsn = Less(val).to_json()
    c1 = Rule.from_json(jsn)
    assert result == c1.satisfied(against)


@pytest.mark.parametrize('val, against, result', [
    ('', '', True),
    ('foo', 'foo', True),
    ('foo', 'fo0', False),
    ('русский', 'русский', True),
    ('русский', 'нет', False),
    ('один', 'один-два', True),
    (1, 1, True),
    (1, 10, True),
    (-30, -20, True),
    (1.0, 1.0, True),
    (1.0, 1.0001, True),
    (1.0001, 1.0, False),
    (50, 50.1, True),
    (50, 50.0, True),
    ('1', '1', True),
    ('1', '3', True),
    ('3', '1', False),
    ((), (), True),
    ((1, 2), (1, 2), True),
    ((1, 2), (1, 2, 3), True),
    ((1, 2, 3), (1, 2), False),
    (['1', '2'], ['1', '2'], True),
    (['1', '2'], ['1', '2', '3'], True),
    ([1, 2], [1, 2, 3], True),
    ([1, 2, 3], [1, 2], False),
    (['1', '2'], ['2', '1'], True),
    (['1', '2'], ['1', '3'], True),
    (['2', '1'], ['1', '2'], False),
    (dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"), True),
    (dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:59", "%Y-%m-%d %H:%M:%S"), True),
    (dt.strptime("2018-01-21 02:37:59", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"), False),
])
def test_greater_or_equal_satisfied(val, against, result):
    c = GreaterOrEqual(val)
    assert result == c.satisfied(against)
    # test after (de)serialization
    jsn = GreaterOrEqual(val).to_json()
    c1 = Rule.from_json(jsn)
    assert result == c1.satisfied(against)


@pytest.mark.parametrize('val, against, result', [
    ('', '', True),
    ('foo', 'foo', True),
    ('foo', 'fo0', True),
    ('русский', 'русский', True),
    ('русский', 'нет', True),
    ('один', 'один-два', False),
    (1, 1, True),
    (1, 10, False),
    (-30, -20, False),
    (1.0, 1.0, True),
    (1.0, 1.0001, False),
    (1.0001, 1.0, True),
    (50, 50.1, False),
    (50, 50.0, True),
    ('1', '1', True),
    ('1', '3', False),
    ('3', '1', True),
    ((), (), True),
    ((1, 2), (1, 2), True),
    ((1, 2), (1, 2, 3), False),
    ((1, 2, 3), (1, 2), True),
    (['1', '2'], ['1', '2'], True),
    (['1', '2'], ['1', '2', '3'], False),
    ([1, 2], [1, 2, 3], False),
    ([1, 2, 3], [1, 2], True),
    (['1', '2'], ['2', '1'], False),
    (['1', '2'], ['1', '3'], False),
    (['2', '1'], ['1', '2'], True),
    (dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"), True),
    (dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:59", "%Y-%m-%d %H:%M:%S"), False),
    (dt.strptime("2018-01-21 02:37:59", "%Y-%m-%d %H:%M:%S"),
     dt.strptime("2018-01-21 02:37:00", "%Y-%m-%d %H:%M:%S"), True),
])
def test_less_or_equal_satisfied(val, against, result):
    c = LessOrEqual(val)
    assert result == c.satisfied(against)
    # test after (de)serialization
    jsn = LessOrEqual(val).to_json()
    c1 = Rule.from_json(jsn)
    assert result == c1.satisfied(against)
