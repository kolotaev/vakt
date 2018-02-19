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
        conditions={
            'ip': CIDRCondition('127.0.0.1/32'),
            'owner': SubjectEqualCondition(),
        },
    ),
    DefaultPolicy(
        id='2',
        description='Allows Max to update any resource',
        effect=ALLOW_ACCESS,
        subjects=['Max'],
        actions=['update'],
        resources=['<.*>'],
    ),
    DefaultPolicy(
        id='3',
        description='Max is not allowed to print any resource',
        effect=DENY_ACCESS,
        subjects=['Max'],
        actions=['print'],
        resources=['<.*>'],
    ),
    DefaultPolicy(
        id='4'
    ),
]
for p in policies:
    pm.create(p)


@pytest.mark.parametrize('req, result', [
    (
        # Empty request carries no information, so nothing is allowed, even empty Policy #4
        Request(),
        False,
    ),
    (
        # Max is allowed to update anything
        Request(
            subject='Max',
            resource='myrn:some.domain.com:resource:123',
            action='update'
        ),
        True,
    ),
    (
        # Max, but not max is allowed to update anything
        Request(
            subject='max',
            resource='myrn:some.domain.com:resource:123',
            action='update'
        ),
        False,
    ),
])
def test_is_allowed(req, result):
    g = Guard(pm, RegexMatcher())
    assert result == g.is_allowed(req)
