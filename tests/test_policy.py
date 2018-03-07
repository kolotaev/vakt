import pytest

from vakt.policy import DefaultPolicy
from vakt.effects import *
from vakt.exceptions import PolicyCreationError
from vakt.rules.net import CIDRRule
from vakt.rules.string import StringEqualRule


def test_properties():
    policy = DefaultPolicy('123', description='readme',
                    subjects=['user'], effect=ALLOW_ACCESS,
                    resources='books:{\d+}', actions=['create', 'delete'], rules={})
    assert '123' == policy.id
    assert 'readme' == policy.description
    assert ['user'] == policy.subjects
    assert ALLOW_ACCESS == policy.effect
    assert 'books:{\d+}' == policy.resources
    assert ['create', 'delete'] == policy.actions
    assert {} == policy.rules


def test_exception_raised_when_rules_is_not_dict():
    with pytest.raises(PolicyCreationError):
        DefaultPolicy('1', rules=[StringEqualRule('foo')])


@pytest.mark.parametrize('data, expect', [
    ('{"id":123}',
     '{"actions": [], "description": null, "effect": "deny", ' +
     '"id": 123, "resources": [], "rules": {}, "subjects": []}'),
    ('{"id":123, "effect":"allow", "actions": ["create", "update"]}',
     '{"actions": ["create", "update"], "description": null, "effect": "allow", "id": 123, ' +
     '"resources": [], "rules": {}, "subjects": []}'),
])
def test_json_roundtrip(data, expect):
    p = DefaultPolicy.from_json(data)
    assert expect == p.to_json()


def test_json_roundtrip_of_a_policy_with_rules():
    p = DefaultPolicy('123', rules={'ip': CIDRRule('192.168.1.0/24'), 'sub': StringEqualRule('test-me')})
    s = p.to_json()
    p1 = DefaultPolicy.from_json(s)
    assert '123' == p1.id
    assert 2 == len(p1.rules)
    assert 'ip' in p1.rules
    assert 'sub' in p1.rules
    assert isinstance(p1.rules['ip'], CIDRRule)
    assert isinstance(p1.rules['sub'], StringEqualRule)
    assert p1.rules['sub'].satisfied('test-me')


@pytest.mark.parametrize('data, exception, msg', [
    ('{}', PolicyCreationError, "'id'"),
    ('{"id":}', ValueError, ''),
    ('', ValueError, ''),
])
def test_json_roundtrip_not_create_policy(data, exception, msg):
    with pytest.raises(exception) as excinfo:
        DefaultPolicy.from_json(data)
    assert msg in str(excinfo.value)


@pytest.mark.parametrize('effect, result', [
    ('foo', False),
    ('', False),
    (None, False),
    (DENY_ACCESS, False),
    (ALLOW_ACCESS, True),
])
def test_allow_access(effect, result):
    p = DefaultPolicy('1', effect=effect)
    assert result == p.allow_access()


def test_start_delimiter():
    p = DefaultPolicy('1')
    assert '<' == p.start_delimiter


def test_end_delimiter():
    p = DefaultPolicy('1')
    assert '>' == p.end_delimiter


def test_pretty_print():
    p = DefaultPolicy('1', description='readme', subjects=['user'])
    assert "<class 'vakt.policy.DefaultPolicy'>" in str(p)
    assert "'id': '1'" in str(p)
    assert "'description': 'readme'" in str(p)
    assert "'subjects': ['user']" in str(p)
    assert "'effect': 'deny'" in str(p)
    assert "'resources': ()" in str(p)
    assert "'actions': ()" in str(p)
    assert "'rules': {}" in str(p)
