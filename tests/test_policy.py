import pytest

from vakt.policy import DefaultPolicy
from vakt.effects import *
from vakt.exceptions import PolicyCreationError
from vakt.conditions.net import CIDRCondition
from vakt.conditions.string import StringEqualCondition


def test_properties():
    policy = DefaultPolicy('123', description='readme',
                    subjects=['user'], effect=ALLOW_ACCESS,
                    resources='books:{\d+}', actions=['create', 'delete'], conditions=[])
    assert '123' == policy.id
    assert 'readme' == policy.description
    assert ['user'] == policy.subjects
    assert ALLOW_ACCESS == policy.effect
    assert 'books:{\d+}' == policy.resources
    assert ['create', 'delete'] == policy.actions
    assert [] == policy.conditions


@pytest.mark.parametrize('data, expect', [
    ('{"id":123}',
     '{"actions": [], "conditions": [], "description": null, "effect": "deny", ' +
     '"id": 123, "resources": [], "subjects": []}'),
    ('{"id":123, "effect":"allow", "actions": ["create", "update"]}',
     '{"actions": ["create", "update"], "conditions": [], "description": null, "effect": "allow", "id": 123, ' +
     '"resources": [], "subjects": []}'),
])
def test_json_roundtrip(data, expect):
    p = DefaultPolicy.from_json(data)
    assert expect == p.to_json()


def test_json_roundtrip_of_a_policy_with_conditions():
    p = DefaultPolicy('123', conditions=[CIDRCondition('192.168.1.0/24'), StringEqualCondition('test-me')])
    s = p.to_json()
    p1 = DefaultPolicy.from_json(s)
    assert '123' == p1.id
    assert 2 == len(p1.conditions)
    assert isinstance(p1.conditions[0], CIDRCondition)
    assert isinstance(p1.conditions[1], StringEqualCondition)
    assert p1.conditions[1].satisfied('test-me')


@pytest.mark.parametrize('data, exception, msg', [
    ('{}', PolicyCreationError, "'id'"),
    ('{"id":}', ValueError, 'value'),
    ('', ValueError, 'value'),
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
