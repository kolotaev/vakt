import pytest

from vakt.policy import Policy
from vakt.effects import ALLOW_ACCESS, DENY_ACCESS
from vakt.exceptions import PolicyCreationError
from vakt.rules.net import CIDR
from vakt.rules.string import Equal
from vakt import TYPE_STRING_BASED, TYPE_RULE_BASED


def test_properties():
    policy = Policy('123', description='readme',
                    subjects=['user'], effect=ALLOW_ACCESS,
                    resources='books:{\d+}', actions=['create', 'delete'], context={})
    assert '123' == policy.uid
    assert 'readme' == policy.description
    assert ['user'] == policy.subjects
    assert ALLOW_ACCESS == policy.effect
    assert 'books:{\d+}' == policy.resources
    assert ['create', 'delete'] == policy.actions
    assert {} == policy.context


def test_exception_raised_when_context_is_not_dict():
    with pytest.raises(PolicyCreationError):
        Policy('1', context=[Equal('foo')])


@pytest.mark.parametrize('data, expect', [
    ('{"uid":123}',
     '{"actions": [], "context": {}, "description": null, "effect": "deny", ' +
     '"resources": [], "subjects": [], "type": 1, "uid": 123}'),
    ('{"effect":"allow", "actions": ["create", "update"], "uid":123}',
     '{"actions": ["create", "update"], "context": {}, "description": null, "effect": "allow", ' +
     '"resources": [], "subjects": [], "type": 1, "uid": 123}'),
    # 'type' if present, should be omitted and not result in setting type of a Policy object
    ('{"actions": ["create", "update"], "uid":123, "type": 2}',
     '{"actions": ["create", "update"], "context": {}, "description": null, "effect": "deny", ' +
     '"resources": [], "subjects": [], "type": 1, "uid": 123}'),
    # 'rules' can be present, but after deserialization should be converted to 'context' field
    ('{"uid":123, "actions": [], "rules":' +
     '{"a": "{\\"type\\": \\"vakt.rules.net.CIDR\\", \\"contents\\": {\\"cidr\\": \\"192.168.2.0/24\\"}}"}}',
     '{"actions": [], ' +
     '"context": {"a": "{\\"type\\": \\"vakt.rules.net.CIDR\\", \\"contents\\": {\\"cidr\\": \\"192.168.2.0/24\\"}}"}, '
     +
     '"description": null, "effect": "deny", "resources": [], "subjects": [], "type": 1, "uid": 123}'),
    # 'context' should be deserialized to 'context' properly
    ('{"uid":123, "actions": [], "rules":' +
     '{"a": "{\\"type\\": \\"vakt.rules.net.CIDR\\", \\"contents\\": {\\"cidr\\": \\"192.168.2.0/24\\"}}"}}',
     '{"actions": [], ' +
     '"context": {"a": "{\\"type\\": \\"vakt.rules.net.CIDR\\", \\"contents\\": {\\"cidr\\": \\"192.168.2.0/24\\"}}"}, '
     +
     '"description": null, "effect": "deny", "resources": [], "subjects": [], "type": 1, "uid": 123}'),
    # 'context' should win over deprecated attribute 'rules' if both are present
    ('{"uid":123, "actions": [], "context":' +
     '{"a": "{\\"type\\": \\"vakt.rules.string.Equal\\", \\"contents\\": {\\"val\\": \\"foo\\"}}"}, ' +
     '"rules": {"b": "{\\"type\\": \\"vakt.rules.net.CIDR\\", \\"contents\\": {\\"cidr\\": \\"192.168.2.0/24\\"}}"}}',
     '{"actions": [], ' +
     '"context": {"a": "{\\"type\\": \\"vakt.rules.string.Equal\\", \\"contents\\": {\\"val\\": \\"foo\\"}}"}, ' +
     '"description": null, "effect": "deny", "resources": [], "subjects": [], "type": 1, "uid": 123}'),
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


def test_json_roundtrip_of_a_policy_with_context():
    p = Policy('123', context={'ip': CIDR('192.168.1.0/24'), 'sub': Equal('test-me')})
    s = p.to_json()
    p1 = Policy.from_json(s)
    assert '123' == p1.uid
    assert 2 == len(p1.context)
    assert 'ip' in p1.context
    assert 'sub' in p1.context
    assert isinstance(p1.context['ip'], CIDR)
    assert isinstance(p1.context['sub'], Equal)
    assert p1.context['sub'].satisfied('test-me')

    # 'context' wins over deprecated rules
    p = Policy(
        '456',
        context={'ip': CIDR('192.168.1.0/24'), 'sub': Equal('foo-bar')},
        rules={'ip': CIDR('127.0.0.1'), 'sub': Equal('baz')}
    )
    s = p.to_json()
    p1 = Policy.from_json(s)
    assert '456' == p1.uid
    assert 2 == len(p1.context)
    assert 'ip' in p1.context
    assert 'sub' in p1.context
    assert isinstance(p1.context['ip'], CIDR)
    assert isinstance(p1.context['sub'], Equal)
    assert p1.context['sub'].satisfied('foo-bar')
    assert p1.context['ip'].satisfied('192.168.1.0')
    assert not hasattr(p1, 'rules')

    # 'rules' are allowed, but they become a 'context' class field
    p = Policy('789', rules={'ip': CIDR('127.0.0.1'), 'sub': Equal('baz')})
    s = p.to_json()
    p1 = Policy.from_json(s)
    assert '789' == p1.uid
    assert 2 == len(p1.context)
    assert 'ip' in p1.context
    assert 'sub' in p1.context
    assert isinstance(p1.context['ip'], CIDR)
    assert isinstance(p1.context['sub'], Equal)
    assert p1.context['sub'].satisfied('baz')
    assert p1.context['ip'].satisfied('127.0.0.1')
    assert not hasattr(p1, 'rules')


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
    assert "'context': {}" in str(p)


@pytest.mark.parametrize('policy, policy_type', [
    (Policy(1), TYPE_STRING_BASED),
    (Policy(1, actions=['<foo.bar>']), TYPE_STRING_BASED),
    (Policy(1, actions=[], resources=[], subjects=[], context={}), TYPE_STRING_BASED),
    (Policy(1, actions=['<foo.bar>'], resources=['asdf']), TYPE_STRING_BASED),
    (Policy(1, actions=['<foo.bar>'], resources=['asdf'], subjects=['<qwerty>']), TYPE_STRING_BASED),
    (Policy(1, actions=['<foo.bar>'], resources=['asdf'], subjects=['<qwerty>'], context={}), TYPE_STRING_BASED),
    (Policy(1, actions=[CIDR('127.0.0.1')]), TYPE_RULE_BASED),
    (Policy(1, actions=[CIDR('127.0.0.1'), '<.*>']), TYPE_RULE_BASED),
    (Policy(1, resources=[CIDR('127.0.0.1'), '<.*>']), TYPE_RULE_BASED),
    (Policy(1, subjects=[CIDR('127.0.0.1'), '<.*>']), TYPE_RULE_BASED),
    (Policy(1, actions=[CIDR('127.0.0.1'), CIDR('10.12.35.88')]), TYPE_RULE_BASED),
    (Policy(1, actions=[CIDR('127.0.0.1')], resources=['asdf']), TYPE_RULE_BASED),
    (Policy(1, actions=[CIDR('127.0.0.1')], resources=[CIDR('127.0.0.1')]), TYPE_RULE_BASED),
    (Policy(1, actions=[CIDR('127.0.0.1')], resources=[CIDR('127.0.0.1')], subjects=['<qwerty>']), TYPE_RULE_BASED),
    (Policy(1, actions=[CIDR('127.0.0.1')], resources=[CIDR('127.0.0.1')], subjects=[CIDR('0.0.0.0')]), TYPE_RULE_BASED)
])
def test_policy_type_on_creation(policy, policy_type):
    assert policy_type == policy.type


def test_policy_type_on_attribute_change():
    p = Policy(1, actions=['<foo.bar>'], resources=['asdf'], subjects=['<qwerty>'])
    assert TYPE_STRING_BASED == p.type
    p.effect = ALLOW_ACCESS
    assert TYPE_STRING_BASED == p.type
    p.actions = [CIDR('0.0.0.0')]
    assert TYPE_RULE_BASED == p.type
    p.subjects = [CIDR('0.0.0.0')]
    assert TYPE_RULE_BASED == p.type
    p.actions = ['<.*>']
    assert TYPE_RULE_BASED == p.type
    p.subjects = ['<.*>']
    assert TYPE_STRING_BASED == p.type
    p.type = TYPE_RULE_BASED  # explicit assign doesn't help
    assert TYPE_STRING_BASED == p.type
