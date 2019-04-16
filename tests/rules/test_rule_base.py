import pytest

from vakt.rules.base import Rule
from vakt.rules.string import Equal
from vakt.exceptions import RuleCreationError
import vakt.rules.net


class ABRule(Rule):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def satisfied(self, what=None, inquiry=None):
        return self.a == self.b


def test_satisfied():
    assert ABRule(2, 2).satisfied()
    assert not ABRule(1, 2).satisfied()


def test_to_json():
    rules = [
        ABRule(1, 2),
        ABRule('x', 'y'),
    ]
    assert '{"a": 1, "b": 2, "py/object": "test_rule_base.ABRule"}' == rules[0].to_json(sort=True)
    assert '{"a": "x", "b": "y", "py/object": "test_rule_base.ABRule"}' == rules[1].to_json(sort=True)


def test_from_json():
    rules = [
        '{"a": 1, "b": 1, "py/object": "test_rule_base.ABRule"}',
        '{"a": "x", "b": "y", "py/object": "test_rule_base.ABRule"}',
    ]
    c1 = Rule.from_json(rules[0])
    c2 = Rule.from_json(rules[1])
    assert isinstance(c1, ABRule)
    assert isinstance(c2, ABRule)
    assert c1.satisfied()
    assert not c2.satisfied()


@pytest.mark.parametrize('rule, satisfied', [
    (ABRule(1, 1), True),
    (ABRule(1, 1.2), False),
    (Equal('foo'), False),
    (vakt.rules.net.CIDR('192.168.0.1/24'), False),
])
def test_json_roundtrip(rule, satisfied):
    c1 = Rule.from_json(rule.to_json())
    assert isinstance(c1, rule.__class__)
    assert c1.__dict__ == rule.__dict__
    assert satisfied == c1.satisfied(None, None)


@pytest.mark.parametrize('data, msg', [
    ("{\"}", "Unterminated string starting"),
])
def test_from_json_fails(data, msg):
    with pytest.raises(RuleCreationError) as excinfo:
        Rule.from_json(data)
    assert msg in str(excinfo.value)


def test_pretty_print():
    c = ABRule(1, 2)
    assert "<class 'test_rule_base.ABRule'>" in str(c)
    assert "'a': 1" in str(c)
    assert "'b': 2" in str(c)
