import pytest

from vakt.policy import Policy
from vakt.effects import ALLOW_ACCESS, DENY_ACCESS
from vakt.exceptions import PolicyCreationError
from vakt.rules.net import CIDRRule
from vakt.rules.string import StringEqualRule


def test_properties():
    policy = Policy('123', description='readme',
                    subjects=['user'], effect=ALLOW_ACCESS,
                    resources='books:{\d+}', actions=['create', 'delete'], rules={})
    assert '123' == policy.uid
    assert 'readme' == policy.description
    assert ['user'] == policy.subjects
    assert ALLOW_ACCESS == policy.effect
    assert 'books:{\d+}' == policy.resources
    assert ['create', 'delete'] == policy.actions
    assert {} == policy.rules


def test_exception_raised_when_rules_is_not_dict():
    with pytest.raises(PolicyCreationError):
        Policy('1', rules=[StringEqualRule('foo')])


@pytest.mark.parametrize('data, expect', [
    ('{"uid":123}',
     '{"actions": [], "description": null, "effect": "deny", ' +
     '"resources": [], "rules": {}, "subjects": [], "type": 1, "uid": 123}'),
    ('{"effect":"allow", "actions": ["create", "update"], "uid":123}',
     '{"actions": ["create", "update"], "description": null, "effect": "allow", ' +
     '"resources": [], "rules": {}, "subjects": [], "type": 1, "uid": 123}'),
    # 'type' if present, should be omitted and not result in setting type of a Policy object
    ('{"actions": ["create", "update"], "uid":123, "type": 2}',
     '{"actions": ["create", "update"], "description": null, "effect": "deny", ' +
     '"resources": [], "rules": {}, "subjects": [], "type": 1, "uid": 123}'),
])
def test_json_roundtrip(data, expect):
    p = Policy.from_json(data)
    assert expect == p.to_json(sort=True)


@pytest.mark.parametrize('data, effect', [
    ('{"uid":123}', DENY_ACCESS),
    ('{"uid":123, "effect":""}', DENY_ACCESS),
    ('{"uid":123, "effect":"deny"}', DENY_ACCESS),
    ('{"uid":123, "effect":null}', DENY_ACCESS),
    ('{"uid":123, "effect":"allow"}', ALLOW_ACCESS),
])
def test_json_default_effect_is_set_correctly_when_from_json(data, effect):
    p = Policy.from_json(data)
    assert effect == p.effect


def test_json_roundtrip_of_a_policy_with_rules():
    p = Policy('123', rules={'ip': CIDRRule('192.168.1.0/24'), 'sub': StringEqualRule('test-me')})
    s = p.to_json()
    p1 = Policy.from_json(s)
    assert '123' == p1.uid
    assert 2 == len(p1.rules)
    assert 'ip' in p1.rules
    assert 'sub' in p1.rules
    assert isinstance(p1.rules['ip'], CIDRRule)
    assert isinstance(p1.rules['sub'], StringEqualRule)
    assert p1.rules['sub'].satisfied('test-me')


@pytest.mark.parametrize('data, exception, msg', [
    ('{}', PolicyCreationError, "'uid'"),
    ('{"uid":}', ValueError, ''),
    ('', ValueError, ''),
])
def test_json_roundtrip_not_create_policy(data, exception, msg):
    with pytest.raises(exception) as excinfo:
        Policy.from_json(data)
    assert msg in str(excinfo.value)


@pytest.mark.parametrize('effect, result', [
    ('foo', False),
    ('', False),
    (None, False),
    (DENY_ACCESS, False),
    (ALLOW_ACCESS, True),
])
def test_allow_access(effect, result):
    p = Policy('1', effect=effect)
    assert result == p.allow_access()


def test_start_tag():
    p = Policy('1')
    assert '<' == p.start_tag


def test_end_tag():
    p = Policy('1')
    assert '>' == p.end_tag


def test_pretty_print():
    p = Policy('1', description='readme', subjects=['user'])
    assert "<class 'vakt.policy.Policy'>" in str(p)
    assert "'uid': '1'" in str(p)
    assert "'description': 'readme'" in str(p)
    assert "'subjects': ['user']" in str(p)
    assert "'effect': 'deny'" in str(p)
    assert "'resources': ()" in str(p)
    assert "'actions': ()" in str(p)
    assert "'rules': {}" in str(p)


@pytest.mark.skip
def test_get_type():
    pass
