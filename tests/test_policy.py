import pytest

from vakt.policy import Policy, PolicyAllow, PolicyDeny
from vakt.effects import ALLOW_ACCESS, DENY_ACCESS
from vakt.exceptions import PolicyCreationError
from vakt.rules.net import CIDR
from vakt.rules.string import Equal
from vakt.rules.operator import Eq, Greater
from vakt.rules.logic import And, Any
from vakt.rules.list import AnyIn
from vakt.policy import TYPE_STRING_BASED, TYPE_RULE_BASED


def test_types():
    assert 1 == TYPE_STRING_BASED
    assert 2 == TYPE_RULE_BASED


def test_properties():
    policy = Policy('123', description='readme',
                    subjects=['user'], effect=ALLOW_ACCESS,
                    resources=r'books:{\d+}', actions=['create', 'delete'], context={})
    assert '123' == policy.uid
    assert 'readme' == policy.description
    assert ['user'] == policy.subjects
    assert ALLOW_ACCESS == policy.effect
    assert r'books:{\d+}' == policy.resources
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
     '{"a": {"py/object": "vakt.rules.net.CIDR", "cidr": "192.168.2.0/24"}}}',
     '{"actions": [], "context": {"a": {"cidr": "192.168.2.0/24", "py/object": "vakt.rules.net.CIDR"}}, ' +
     '"description": null, "effect": "deny", "resources": [], "subjects": [], "type": 1, "uid": 123}'),
    # 'context' should be deserialized to 'context' properly
    ('{"uid":123, "actions": [], "rules":' +
     '{"a": {"py/object": "vakt.rules.net.CIDR", "cidr": "192.168.2.0/24"}}}',
     '{"actions": [], "context": {"a": {"cidr": "192.168.2.0/24", "py/object": "vakt.rules.net.CIDR"}}, ' +
     '"description": null, "effect": "deny", "resources": [], "subjects": [], "type": 1, "uid": 123}'),
    # 'context' should win over deprecated attribute 'rules' if both are present
    ('{"uid":123, "actions": [], "context": {"a": {"py/object": "vakt.rules.string.Equal", "val": "foo"}}, ' +
     '"rules": {"b": {"cidr": "192.168.2.0/24", "py/object": "vakt.rules.net.CIDR"}}}',
     '{"actions": [], "context": {"a": {"py/object": "vakt.rules.string.Equal", "val": "foo"}}, ' +
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
    with pytest.deprecated_call():
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


@pytest.mark.parametrize('policy', [
    Policy(1, subjects=[{'name': Eq('Max'), 'rate': Greater(90)}], actions=[Eq('get'), Eq('post')], resources=[Any()]),
    Policy(2, subjects=[{'login': Eq('sally')}], actions=[Eq('get'), Eq('post')], context={'ip': Eq('127.0.0.1')}),
    Policy(3, subjects=[{'rating': AnyIn(1, 2)}], actions=[And(Eq('get'), Eq('post'))]),
    Policy(4, subjects=[{'rating': AnyIn(1, 2)}], actions=[And(Eq('get'), Eq('post'))]),
    Policy(5, actions=[Eq('get')]),
])
def test_json_roundtrip_of_a_rules_based_policy(policy):
    pj = policy.to_json()
    p2 = Policy.from_json(pj)
    assert policy.to_json() == p2.to_json()


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
    p = Policy('2', actions=[Eq('get'), Eq('post')])
    assert "vakt.rules.operator.Eq" in str(p.actions)


@pytest.mark.parametrize('policy, policy_type', [
    (Policy(1), TYPE_STRING_BASED),
    (Policy(1, actions=['<foo.bar>']), TYPE_STRING_BASED),
    (Policy(1, actions=[], resources=[], subjects=[], context={}), TYPE_STRING_BASED),
    (Policy(1, actions=['<foo.bar>'], resources=['asdf']), TYPE_STRING_BASED),
    (Policy(1, actions=['<foo.bar>'], resources=['asdf'], subjects=['<qwerty>']), TYPE_STRING_BASED),
    (Policy(1, actions=['<foo.bar>'], resources=['asdf'], subjects=['<qwerty>'], context={}), TYPE_STRING_BASED),
    (Policy(1, actions=['books:<foo.bar>'], resources=['asdf'], subjects=['<qwerty>'], context={}), TYPE_STRING_BASED),
    (Policy(1, actions=[{'ip': CIDR('127.0.0.1')}]), TYPE_RULE_BASED),
    (Policy(1, actions=[Eq('get')]), TYPE_RULE_BASED),
    (Policy(1, actions=[Eq('get'), {'read': Eq(True)}]), TYPE_RULE_BASED),
    (Policy(1, actions=[{'ip': CIDR('127.0.0.1')}, {'ip': CIDR('10.12.35.88')}]), TYPE_RULE_BASED),
    (Policy(1, actions=[{'ip': CIDR('127.0.0.1')}], resources=[{'ip': CIDR('127.0.0.1')}]), TYPE_RULE_BASED),
    (Policy(1, actions=[{'ip': CIDR('127.0.0.1')}],
            resources=[{'ip': CIDR('127.0.0.1')}], subjects=[{'ip': CIDR('0.0.0.0')}]), TYPE_RULE_BASED),
    (Policy(1, subjects=[{'name': Eq('Max'), 'rate': Greater(90)}], actions=[Eq('get'), Eq('post')],
            resources=[{'ip': CIDR('127.0.0.1')}]), TYPE_RULE_BASED)
])
def test_policy_type_on_creation(policy, policy_type):
    assert policy_type == policy.type


@pytest.mark.parametrize('policy_data', [
    {'uid': 1, 'actions': [{'ip': CIDR('127.0.0.1')}, '<.*>']},
    {'uid': 1, 'resources': [{'ip': CIDR('127.0.0.1')}, '<.*>']},
    {'uid': 1, 'subjects': [{'ip': CIDR('127.0.0.1')}, '<.*>']},
    {'uid': 1, 'subjects': [{'ip': CIDR('127.0.0.1')}, '<.*>'], 'resources': ['asdf']},
    {'uid': 1, 'subjects': [{'ip': CIDR('127.0.0.1')}], 'resources': ['<asdf>']},
    {'uid': 1, 'subjects': [{'ip': CIDR('127.0.0.1')}], 'actions': ['foo']},
    {'uid': 1, 'subjects': [Eq('Molly')], 'actions': ['foo']},
    {'uid': 1, 'subjects': ['Jane'], 'actions': [Eq('run')]},
])
def test_policy_raises_exception_if_mixed_elements(policy_data):
    with pytest.raises(PolicyCreationError):
        Policy(**policy_data)


def test_policy_type_on_attribute_change():
    p = Policy(1, actions=['<foo.bar>'], resources=['asdf'], subjects=['<qwerty>'])
    assert TYPE_STRING_BASED == p.type
    p.effect = ALLOW_ACCESS
    assert TYPE_STRING_BASED == p.type
    with pytest.raises(PolicyCreationError):
        p.actions = [{'ip': CIDR('0.0.0.0')}]
    assert TYPE_STRING_BASED == p.type
    with pytest.raises(PolicyCreationError):
        p.subjects = [{'ip': CIDR('0.0.0.0')}]
    with pytest.raises(PolicyCreationError):
        p.actions = [Any()]
    assert TYPE_STRING_BASED == p.type
    p.actions = ['<.*>']
    assert TYPE_STRING_BASED == p.type
    p.subjects = ['<.*>']
    assert TYPE_STRING_BASED == p.type
    p.type = TYPE_RULE_BASED  # explicit assign doesn't help
    assert TYPE_STRING_BASED == p.type
    # testing the from the opposite direction
    p = Policy(2, actions=[Any()], resources=[{'book': Eq('UX Manual')}], subjects=[Eq('Sally'), Eq('Bob')])
    assert TYPE_RULE_BASED == p.type
    p.effect = ALLOW_ACCESS
    assert TYPE_RULE_BASED == p.type
    with pytest.raises(PolicyCreationError):
        p.actions = ['<foo.bar>']
    assert TYPE_RULE_BASED == p.type
    with pytest.raises(PolicyCreationError):
        p.subjects = ['<foo.bar>', 'baz']
    with pytest.raises(PolicyCreationError):
        p.actions = ['baz<.*>']
    assert TYPE_RULE_BASED == p.type
    p.actions = [Any()]
    assert TYPE_RULE_BASED == p.type
    p.subjects = [Any()]
    assert TYPE_RULE_BASED == p.type
    p.type = TYPE_STRING_BASED  # explicit assign doesn't help
    assert TYPE_RULE_BASED == p.type


@pytest.mark.parametrize('args, msg', [
    ({'actions': (1, 2)}, 'Field "actions" element must be of `str`, `dict` or `Rule` type.'),
    ({'actions': (1, 'abc')}, 'Field "actions" element must be of `str`, `dict` or `Rule` type.'),
    ({'actions': ('2', 1)}, 'Field "actions" element must be of `str`, `dict` or `Rule` type.'),
    ({'actions': ([3])}, 'Field "actions" element must be of `str`, `dict` or `Rule` type.'),
    ({'actions': ([], [])}, 'Field "actions" element must be of `str`, `dict` or `Rule` type.'),
    ({'subjects': (1, {})}, 'Field "subjects" element must be of `str`, `dict` or `Rule` type'),
    ({'context': ()}, 'Error creating Policy. Context must be a dictionary'),
    ({'context': 5}, 'Error creating Policy. Context must be a dictionary'),
    ({'context': 'data'}, 'Error creating Policy. Context must be a dictionary'),
])
def test_policy_field_type_check(args, msg):
    with pytest.raises(PolicyCreationError) as excinfo:
        Policy(1, **args)
    assert msg in str(excinfo.value)


@pytest.mark.parametrize('klass, is_allowed, effect', [
    (PolicyAllow, True, 'allow'),
    (PolicyDeny, False, 'deny'),
])
def test_PolicyAllow_and_PolicyDeny(klass, is_allowed, effect):
    p = klass(1, actions=['<foo.bar>'], resources=['asdf'],
              subjects=['<qwerty>'], description='test')
    assert is_allowed == p.allow_access()
    assert 1 == p.uid
    assert 'test' == p.description
    assert TYPE_STRING_BASED == p.type
    assert ['<foo.bar>'] == p.actions
    assert ['asdf'] == p.resources
    assert ['<qwerty>'] == p.subjects
    assert {} == p.context
    assert '{"actions": ["<foo.bar>"], "context": {}, "description": "test", "effect": "%s", ' % effect + \
           '"resources": ["asdf"], "subjects": ["<qwerty>"], "type": 1, "uid": 1}' == p.to_json(sort=True)
    assert ['<foo.bar>'] == Policy.from_json(p.to_json()).actions
    p.effect = DENY_ACCESS
    assert DENY_ACCESS == p.effect
    p2 = klass(2, context={'a': Eq(100)})
    assert isinstance(p2.context.get('a'), Eq)
    assert 100 == p2.context.get('a').val
    # check positional arguments
    p3 = Policy(1, actions=['<foo.bar>'], resources=['asdf'],
                subjects=['<qwerty>'], description='test', effect=ALLOW_ACCESS if is_allowed else DENY_ACCESS)
    p4 = klass(1, ['<qwerty>'], ['asdf'], ['<foo.bar>'], {}, 'test')
    assert p3.to_json(sort=True) == p4.to_json(sort=True)
