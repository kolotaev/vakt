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
        description="""Max, Peter, Zac, Ken are allowed to create, delete, get the resources 
        only if the client IP matches and the request states that any of them is the resource owner""",
        effect=ALLOW_ACCESS,
        subjects=('Max', 'Peter', '<Zac|Ken>'),
        resources=('myrn:some.domain.com:resource:123', 'myrn:some.domain.com:resource:345', 'myrn:something:foo:<.+>'),
        actions=('<create|delete>', 'get'),
        conditions=(
            CIDRCondition('127.0.0.1/32'),
            SubjectEqualCondition(),
        ),
    ),
    DefaultPolicy(
        id='2',
        description='Allows Max to update any resource',
        effect=ALLOW_ACCESS,
        subjects=['max'],
        actions=['update'],
        resources=['<.*>'],
    ),
    DefaultPolicy(
        id='3',
        description='Max is not allowed to print any resource',
        effect=DENY_ACCESS,
        subjects=['max'],
        actions=['print'],
        resources=['<.*>'],
    ),
]
for p in policies:
    pm.create(p)


@pytest.mark.parametrize('req, result', [
    (
            Request(),
            False,
    ),
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
