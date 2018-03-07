import pytest

from vakt.matcher import RegexMatcher
from vakt.managers.memory import MemoryManager
from vakt.rules.net import CIDRRule
from vakt.rules.request import SubjectEqualRule
from vakt.effects import DENY_ACCESS, ALLOW_ACCESS
from vakt.policy import DefaultPolicy
from vakt.guard import Guard, Request


# Create all required test policies
pm = MemoryManager()
policies = [
    DefaultPolicy(
        id='1',
        description="""
        Max, Nina, Ben, Henry are allowed to create, delete, get the resources 
        only if the client IP matches and the request states that any of them is the resource owner
        """,
        effect=ALLOW_ACCESS,
        subjects=('Max', 'Nina', '<Ben|Henry>'),
        resources=('myrn:example.com:resource:123', 'myrn:example.com:resource:345', 'myrn:something:foo:<.+>'),
        actions=('<create|delete>', 'get'),
        rules={
            'ip': CIDRRule('127.0.0.1/32'),
            'owner': SubjectEqualRule(),
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
    DefaultPolicy(
        id='5',
        description='Allows Nina to update any resources that have only digits',
        effect=ALLOW_ACCESS,
        subjects=['Nina'],
        actions=['update'],
        resources=['<[\d]+>'],
    ),
]
for p in policies:
    pm.create(p)


@pytest.mark.parametrize('desc, req, should_be_allowed', [
    (
        'Empty request carries no information, so nothing is allowed, even empty Policy #4',
        Request(),
        False,
    ),
    (
        'Max is allowed to update anything',
        Request(
            subject='Max',
            resource='myrn:example.com:resource:123',
            action='update'
        ),
        True,
    ),
    (
        'Max is allowed to update anything, even empty one',
        Request(
            subject='Max',
            resource='',
            action='update'
        ),
        True,
    ),
    (
        'Max, but not max is allowed to update anything (case-sensitive comparison)',
        Request(
            subject='max',
            resource='myrn:example.com:resource:123',
            action='update'
        ),
        False,
    ),
    (
        'Max is not allowed to print anything',
        Request(
            subject='Max',
            resource='myrn:example.com:resource:123',
            action='print',
        ),
        False,
    ),
    (
        'Max is not allowed to print anything, even if no resource is given',
        Request(
            subject='Max',
            action='print'
        ),
        False,
    ),
    (
        'Max is not allowed to print anything, even an empty resource',
        Request(
            subject='Max',
            action='print',
            resource=''
        ),
        False,
    ),
    (
        'Policy #1 matches and has allow-effect',
        Request(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Nina',
                'ip': '127.0.0.1'
            }
        ),
        True,
    ),
    (
        'Policy #1 matches - Henry is listed in the allowed subjects regexp',
        Request(
            subject='Henry',
            action='get',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Henry',
                'ip': '127.0.0.1'
            }
        ),
        True,
    ),
    (
        'Policy #1 does not match - one of the contexts was not found (misspelled)',
        Request(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Nina',
                'IP': '127.0.0.1'
            }
        ),
        False,
    ),
    (
        'Policy #1 does not match - one of the contexts is missing',
        Request(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'ip': '127.0.0.1'
            }
        ),
        False,
    ),
    (
        'Policy #1 does not match - context says that owner is Ben, not Nina',
        Request(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Ben',
                'ip': '127.0.0.1'
            }
        ),
        False,
    ),
    (
        'Policy #1 does not match - context says IP is not in the allowed range',
        Request(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Nina',
                'ip': '0.0.0.0'
            }
        ),
        False,
    ),
    (
        'Policy #5 does not match - action is update, but subjects does not match',
        Request(
            subject='Sarah',
            action='update',
            resource='88',
        ),
        False,
    ),
    (
        'Policy #5 does not match - action is update, subject is Nina, but resource-name is not digits',
        Request(
            subject='Nina',
            action='update',
            resource='abcd',
        ),
        False,
    ),
])
def test_is_allowed(desc, req, should_be_allowed):
    g = Guard(pm, RegexMatcher())
    assert should_be_allowed == g.is_allowed(req)


def test_is_allowed_for_none_policies():
    g = Guard(MemoryManager(), RegexMatcher())
    assert not g.is_allowed(Request(subject='foo', action='bar', resource='baz'))


def test_guard_if_unexpected_exception_raised():
    # for testing unexpected exception
    class BadMemoryManager(MemoryManager):
        def find_by_request(self, request=None):
            raise Exception('This is test class that raises errors')
    pm = BadMemoryManager()
    g = Guard(pm, RegexMatcher())
    assert not g.is_allowed(Request(subject='foo', action='bar', resource='baz'))
