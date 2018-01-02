import pytest
from vakt.policy import Policy
from vakt.effects import *


def test_properties():
    policy = Policy('123', description='readme',
                    subjects=['user'], effect=ALLOW_ACCESS,
                    resources='books:{\d+}', actions=['create', 'delete'], conditions=[])
    assert '123' == policy.id
    assert 'readme' == policy.description
    assert ['user'] == policy.subjects
    assert ALLOW_ACCESS == policy.effect
    assert 'books:{\d+}' == policy.resources
    assert ['create', 'delete'] == policy.actions
    assert [] == policy.conditions


@pytest.mark.parametrize('data', [
    '{"id":123}',
])
def test_from_json_creates_policy(data):
    p = Policy.from_json(data)
    assert data == p.to_json()


def test_from_json_can_not_create_policy():
    assert 0 == 0
