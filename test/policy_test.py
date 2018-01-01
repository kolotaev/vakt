from vakt.policy import Policy
from vakt.effects import *


def test_properties():
    policy = Policy(id='123', description='readme',
                    subjects=['user'], effect=ALLOW_ACCESS,
                    resources='books:{\d+}', actions=['create', 'delete'], conditions=[])
    assert '123' == policy.id
    assert 'readme' == policy.description
    assert ['user'] == policy.subjects
    assert ALLOW_ACCESS == policy.effect
    assert 'books:{\d+}' == policy.resources
    assert ['create', 'delete'] == policy.actions
    assert [] == policy.conditions
