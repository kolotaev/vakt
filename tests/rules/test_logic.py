import pytest

from vakt.rules.logic import *
from vakt.rules.base import Rule
from vakt.rules.operator import Greater, Less, Eq
from vakt.rules.inquiry import ActionEqual
from vakt.rules.list import In
from vakt.guard import Inquiry


@pytest.mark.parametrize('against, result', [
    ('', False),
    ('a', True),
    ([], False),
    ([1], True),
    (0, False),
    (1, True),
    (None, False),
    (1 < 90, True),
    (1 > 90, False),
    (lambda: True, True),
    (lambda: False, False),
])
def test_truthy_satisfied(against, result):
    assert result == Truthy().satisfied(against)
    # test after (de)serialization
    jsn = Truthy().to_json()
    assert result == Rule.from_json(jsn).satisfied(against)


@pytest.mark.parametrize('against, result', [
    ('', True),
    ('a', False),
    ([], True),
    ([1], False),
    (0, True),
    (1, False),
    (None, True),
    (1 < 90, False),
    (1 > 90, True),
    (lambda: True, False),
    (lambda: False, True),
])
def test_falsy_satisfied(against, result):
    assert result == Falsy().satisfied(against)
    # test after (de)serialization
    jsn = Falsy().to_json()
    assert result == Rule.from_json(jsn).satisfied(against)


def test_and_or_rules_bad_args():
    expected_msg = "Arguments should be of Rule class or it's derivatives"
    with pytest.raises(TypeError) as excinfo:
        And(Inquiry())
    assert expected_msg in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        Or(Inquiry(), 123)
    assert expected_msg in str(excinfo.value)


@pytest.mark.parametrize('rules, what, inquiry, result', [
    ([], 1, None, False),
    ([Greater(-1)], 1, None, True),
    ([Greater(55)], 1, None, False),
    ([Greater(-1), Less(10)], 1, None, True),
    ([Greater(-1), Less(10), Eq(700)], 1, None, False),
    ([Eq('read'), In('read', 'write'), ActionEqual()], 'read', Inquiry(action='read'), True),
    ([Eq('read'), In('write'), ActionEqual()], 'read', Inquiry(action='read'), False),
])
def test_and_rule(rules, what, inquiry, result):
    r = And(*rules)
    assert result == r.satisfied(what, inquiry)
    # test after (de)serialization
    assert result == Rule.from_json(And(*rules).to_json()).satisfied(what, inquiry)


@pytest.mark.parametrize('rules, what, inquiry, result', [
    ([], 1, None, False),
    ([Greater(-1)], 1, None, True),
    ([Greater(55)], 1, None, False),
    ([Greater(-1), Less(10)], 1, None, True),
    ([Less(10), Eq(700)], 1, None, True),
    ([Eq(700), Less(10)], 1, None, True),
    ([Eq('read'), In('read', 'write'), ActionEqual()], 'read', Inquiry(action='read'), True),
    ([Eq('read'), In('write'), ActionEqual()], 'read', Inquiry(action='read'), True),
])
def test_or_rule(rules, what, inquiry, result):
    r = Or(*rules)
    assert result == r.satisfied(what, inquiry)
    # test after (de)serialization
    assert result == Rule.from_json(Or(*rules).to_json()).satisfied(what, inquiry)


def test_or_rule_uses_short_circuit_but_and_rule_does_not():
    x = []
    def get_inc(x):
        def inc():
            x.append(1)
            return True
        return inc
    f = get_inc(x)
    rules = [
        Eq(f),
        Truthy()
    ]
    # test Or
    r = Or(*rules)
    assert r.satisfied(f, None)
    assert r.satisfied(f, None)
    assert 0 == len(x)
    # test And
    r = And(*rules)
    assert r.satisfied(f, None)
    assert 1 == len(x)
    assert r.satisfied(f, None)
    assert 2 == len(x)


def test_not_rule_bad_args():
    expected_msg = "Arguments should be of Rule class or it's derivatives"
    with pytest.raises(TypeError) as excinfo:
        Not(123)
    assert expected_msg in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        Not([Greater(-1)])
    assert expected_msg in str(excinfo.value)


@pytest.mark.parametrize('rule, what, inquiry, result', [
    (Greater(-1), 1, None, False),
    (Greater(55), 1, None, True),
    (Less(10), 1, None, False),
    (Eq(10), 10, None, False),
    (Eq(10), 11, None, True),
    (ActionEqual(), 'read', Inquiry(action='read'), False),
    (ActionEqual(), 'write', Inquiry(action='read'), True),
])
def test_not_rule(rule, what, inquiry, result):
    r = Not(rule)
    assert result == r.satisfied(what, inquiry)
    # test after (de)serialization
    assert result == Rule.from_json(Not(rule).to_json()).satisfied(what, inquiry)


@pytest.mark.parametrize('what', [
    1,
    'str',
    9.0,
    False,
    True,
])
def test_any_and_neither_rules(what):
    assert Any().satisfied(what)
    assert not Neither().satisfied(what)
    # test after (de)serialization
    assert Rule.from_json(Any().to_json()).satisfied(what)
    assert not Rule.from_json(Neither().to_json()).satisfied(what)
