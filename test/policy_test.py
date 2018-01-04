import pytest
import json
from vakt.policy import DefaultPolicy
from vakt.effects import *
from vakt.exceptions import PolicyCreationError


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
     '{"id": 123, "description": null, ' +
     '"subjects": [], "effect": "deny", "resources": [], "actions": [], "conditions": []}'),
    ('{"id":123, "effect":"allow", "actions": ["create", "update"]}',
     '{"id": 123, "description": null, ' +
     '"subjects": [], "effect": "allow", "resources": [], "actions": ["create", "update"], "conditions": []}'),
])
def test_from_to_json_round_trip(data, expect):
    p = DefaultPolicy.from_json(data)
    assert expect == p.to_json()


@pytest.mark.parametrize('data, exception, msg', [
    ('{}', PolicyCreationError, "'id'"),
    ('{"id":}', json.JSONDecodeError, 'value'),
    ('', json.JSONDecodeError, 'value'),
])
def test_from_json_can_not_create_policy(data, exception, msg):
    with pytest.raises(exception) as excinfo:
        DefaultPolicy.from_json(data)
    assert msg in str(excinfo.value)
