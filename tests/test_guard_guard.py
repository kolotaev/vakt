import pytest

from vakt.matcher import RegexMatcher
from vakt.managers.memory import MemoryManager
from vakt.conditions.net import CIDRCondition
from vakt.conditions.request import SubjectEqualCondition
from vakt.effects import DENY_ACCESS, ALLOW_ACCESS
from vakt.policy import DefaultPolicy
from vakt.guard import Guard, Request


# Create all required test policies
pm = MemoryManager()
policies = [
    DefaultPolicy(
        id='1',
        description='max, peter, zac, ken are allowed to create, delete, get the resources ',
        effect=ALLOW_ACCESS,
        subjects=('max', 'peter', '<zac|ken>'),
        resources=('myrn:some.domain.com:resource:123', 'myrn:some.domain.com:resource:345', 'myrn:something:foo:<.+>'),
        actions=('<create|delete>', 'get'),
        conditions=(
            CIDRCondition('127.0.0.1/32'),
            SubjectEqualCondition(),
        )
    ),
    # DefaultPolicy(
    #     id='2'
    # ),
]
for p in policies:
    pm.create(p)


@pytest.mark.parametrize('req, result', [
    (
        Request(
            resource='any',
            action='get',
            subject='max'
        ),
        False,
    ),
])
def test_is_allowed(req, result):
    g = Guard(pm, RegexMatcher())
    assert result == g.is_allowed(req)
