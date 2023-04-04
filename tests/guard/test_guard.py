import logging
import io
import re
import sys

import pytest

from vakt.checker import RegexChecker, RulesChecker
from vakt.storage.memory import MemoryStorage
from vakt.rules.net import CIDR
from vakt.rules.inquiry import SubjectEqual, SubjectMatch, ResourceMatch
from vakt.effects import DENY_ACCESS, ALLOW_ACCESS
from vakt.policy import Policy
from vakt.guard import Guard, Inquiry
from vakt.rules.operator import Eq
from vakt.rules.string import RegexMatch
from vakt.rules.logic import Not, And, Any
from vakt.rules.list import In


@pytest.fixture()
def logger():
    log = logging.getLogger('vakt.guard')
    initial_handlers = log.handlers[:]
    initial_level = log.getEffectiveLevel()
    yield log
    log.handlers = initial_handlers
    log.setLevel(initial_level)


@pytest.mark.parametrize('desc, inquiry, should_be_allowed, checker', [
    (
        'Empty inquiry carries no information, so nothing is allowed, even empty Policy #4',
        Inquiry(),
        False,
        RegexChecker(),
    ),
    (
        'Max is allowed to update anything',
        Inquiry(
            subject='Max',
            resource='myrn:example.com:resource:123',
            action='update'
        ),
        True,
        RegexChecker(),
    ),
    (
        'Max is allowed to update anything, even empty one',
        Inquiry(
            subject='Max',
            resource='',
            action='update'
        ),
        True,
        RegexChecker(),
    ),
    (
        'Max, but not max is allowed to update anything (case-sensitive comparison)',
        Inquiry(
            subject='max',
            resource='myrn:example.com:resource:123',
            action='update'
        ),
        False,
        RegexChecker(),
    ),
    (
        'Max is not allowed to print anything',
        Inquiry(
            subject='Max',
            resource='myrn:example.com:resource:123',
            action='print',
        ),
        False,
        RegexChecker(),
    ),
    (
        'Max is not allowed to print anything, even if no resource is given',
        Inquiry(
            subject='Max',
            action='print'
        ),
        False,
        RegexChecker(),
    ),
    (
        'Max is not allowed to print anything, even an empty resource',
        Inquiry(
            subject='Max',
            action='print',
            resource=''
        ),
        False,
        RegexChecker(),
    ),
    (
        'Policy #1 matches and has allow-effect',
        Inquiry(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Nina',
                'ip': '127.0.0.1'
            }
        ),
        True,
        RegexChecker(),
    ),
    (
        'Policy #1 matches - Henry is listed in the allowed subjects regexp',
        Inquiry(
            subject='Henry',
            action='get',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Henry',
                'ip': '127.0.0.1'
            }
        ),
        True,
        RegexChecker(),
    ),
    (
        'Policy #1 does not match - Henry is listed in the allowed subjects regexp. But usage of inappropriate checker',
        Inquiry(
            subject='Henry',
            action='get',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Henry',
                'ip': '127.0.0.1'
            }
        ),
        False,
        RulesChecker(),
    ),
    (
        'Policy #1 does not match - one of the contexts was not found (misspelled)',
        Inquiry(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Nina',
                'IP': '127.0.0.1'
            }
        ),
        False,
        RegexChecker(),
    ),
    (
        'Policy #1 does not match - one of the contexts is missing',
        Inquiry(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'ip': '127.0.0.1'
            }
        ),
        False,
        RegexChecker(),
    ),
    (
        'Policy #1 does not match - context says that owner is Ben, not Nina',
        Inquiry(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Ben',
                'ip': '127.0.0.1'
            }
        ),
        False,
        RegexChecker(),
    ),
    (
        'Policy #1 does not match - context says IP is not in the allowed range',
        Inquiry(
            subject='Nina',
            action='delete',
            resource='myrn:example.com:resource:123',
            context={
                'owner': 'Nina',
                'ip': '0.0.0.0'
            }
        ),
        False,
        RegexChecker(),
    ),
    (
        'Policy #5 does not match - action is update, but subjects does not match',
        Inquiry(
            subject='Sarah',
            action='update',
            resource='88',
        ),
        False,
        RegexChecker(),
    ),
    (
        'Policy #5 does not match - action is update, subject is Nina, but resource-name is not digits',
        Inquiry(
            subject='Nina',
            action='update',
            resource='abcd',
        ),
        False,
        RegexChecker(),
    ),
    (
        'Policy #6 does not match - Inquiry has wrong format for resource',
        Inquiry(
            subject='Nina',
            action='update',
            resource='abcd',
        ),
        False,
        RulesChecker(),
    ),
    (
        'Policy #6 does not match - Inquiry has string ID for resource',
        Inquiry(
            subject='Nina',
            action='read',
            resource={'id': 'abcd'},
        ),
        False,
        RulesChecker(),
    ),
    (
        'Policy #6 should match',
        Inquiry(
            subject='Nina',
            action='read',
            resource={'id': '00678', 'magazine': 'Playboy1'},
        ),
        True,
        RulesChecker(),
    ),
    (
        'Policy #6 should not match - usage of inappropriate checker',
        Inquiry(
            subject='Nina',
            action='read',
            resource={'id': '00678', 'magazine': 'Playboy1'},
        ),
        False,
        RegexChecker(),
    ),
])
def test_is_allowed(desc, inquiry, should_be_allowed, checker):
    # Create all required test policies
    st = MemoryStorage()
    policies = [
        Policy(
            uid='1',
            description="""
            Max, Nina, Ben, Henry are allowed to create, delete, get the resources
            only if the client IP matches and the inquiry states that any of them is the resource owner
            """,
            effect=ALLOW_ACCESS,
            subjects=('Max', 'Nina', '<Ben|Henry>'),
            resources=('myrn:example.com:resource:123', 'myrn:example.com:resource:345', 'myrn:something:foo:<.+>'),
            actions=('<create|delete>', 'get'),
            context={
                'ip': CIDR('127.0.0.1/32'),
                'owner': SubjectEqual(),
            },
        ),
        Policy(
            uid='2',
            description='Allows Max to update any resource',
            effect=ALLOW_ACCESS,
            subjects=['Max'],
            actions=['update'],
            resources=['<.*>'],
        ),
        Policy(
            uid='3',
            description='Max is not allowed to print any resource',
            effect=DENY_ACCESS,
            subjects=['Max'],
            actions=['print'],
            resources=['<.*>'],
        ),
        Policy(
            uid='4'
        ),
        Policy(
            uid='5',
            description='Allows Nina to update any resources that have only digits',
            effect=ALLOW_ACCESS,
            subjects=['Nina'],
            actions=['update'],
            resources=[r'<[\d]+>'],
        ),
        Policy(
            uid='6',
            description='Allows Nina to update any resources that have only digits. Defined by rules',
            effect=ALLOW_ACCESS,
            subjects=[Eq('Nina')],
            actions=[Eq('update'), Eq('read')],
            resources=[{'id': RegexMatch(r'\d+'), 'magazine': RegexMatch(r'[\d\w]+')}],
        ),
    ]
    for p in policies:
        st.add(p)
    g = Guard(st, checker)
    assert should_be_allowed == g.is_allowed(inquiry)


def test_is_allowed_for_none_policies():
    g = Guard(MemoryStorage(), RegexChecker())
    assert not g.is_allowed(Inquiry(subject='foo', action='bar', resource='baz'))


def test_not_allowed_when_similar_policies_have_at_least_one_deny_access():
    st = MemoryStorage()
    policies = (
        Policy(
            uid='1',
            effect=ALLOW_ACCESS,
            subjects=['foo'],
            actions=['bar'],
            resources=['baz'],
        ),
        Policy(
            uid='2',
            effect=DENY_ACCESS,
            subjects=['foo'],
            actions=['bar'],
            resources=['baz'],
        ),
    )
    for p in policies:
        st.add(p)
    g = Guard(st, RegexChecker())
    assert not g.is_allowed(Inquiry(subject='foo', action='bar', resource='baz'))


def test_guard_if_unexpected_exception_raised():
    # for testing unexpected exception
    class BadMemoryStorage(MemoryStorage):
        def find_for_inquiry(self, inquiry=None, checker=None):
            raise Exception('This is test class that raises errors')
    g = Guard(BadMemoryStorage(), RegexChecker())
    assert not g.is_allowed(Inquiry(subject='foo', action='bar', resource='baz'))


@pytest.mark.parametrize('desc, policy, inquiry, result', [
    (
        'match for non-attribute',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[SubjectMatch()],
            resources=[Any()],
        ),
        Inquiry(subject='b', action='b', resource='a'),
        True,
    ),
    (
        'not match for non-attribute',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[SubjectMatch()],
            resources=[Any()],
        ),
        Inquiry(subject='b', action='c', resource='a'),
        False,
    ),
    (
        'match for non-attribute composition of rules (negate SubjectMatch)',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[Not(SubjectMatch())],
            resources=[Any()],
        ),
        Inquiry(subject='b', action='c', resource='a'),
        True,
    ),
    (
        'match for non-attribute composition of rules (and SubjectMatch)',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[And(In('b', 'd'), SubjectMatch())],
            resources=[Any()],
        ),
        Inquiry(subject='b', action='b', resource='a'),
        True,
    ),
    (
        'match for attribute; itself is not an attribute',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[SubjectMatch('letter')],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'b'}, action='b', resource='d'),
        True,
    ),
    (
        'not match for attribute; itself is not an attribute. wrong attribute - case sensitive',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[SubjectMatch('Letter')],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'b'}, action='b', resource='d'),
        False,
    ),
    (
        'not match for attribute; itself is not an attribute. wrong attribute',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[SubjectMatch('sign')],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'b'}, action='b', resource='d'),
        False,
    ),
    (
        'not match for attribute; itself is not an attribute. attribute contains not expected value',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[SubjectMatch('letter')],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'a'}, action='b', resource='d'),
        False,
    ),
    (
        'not match for attribute; itself is not an attribute; itself contains not expected value in attribute',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[SubjectMatch('letter')],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'b'}, action='bbb', resource='d'),
        False,
    ),
    (
        'match for attribute; itself is not an attribute; several attributes',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[SubjectMatch('letter')],
            resources=[Any()],
        ),
        Inquiry(subject={'sign': '+', 'letter': 'b', 'digit': 90}, action='b', resource='d'),
        True,
    ),
    (
        'match for attribute; itself is an attribute',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[{'section': SubjectMatch('letter')}],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'b'}, action={'section': 'b'}, resource='d'),
        True,
    ),
    (
        'not match for attribute; itself is an attribute; wrong value in action',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[{'section': SubjectMatch('letter')}],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'b'}, action={'section': 'bbb'}, resource='d'),
        False,
    ),
    (
        'not match for attribute; itself is an attribute; wrong value in subject',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[{'section': SubjectMatch('letter')}],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'a'}, action={'section': 'b'}, resource='d'),
        False,
    ),
    (
        'not match for attribute; itself is an attribute; wrong attribute in action',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[{'section': SubjectMatch('letter')}],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'a'}, action={'sub-section': 'a'}, resource='d'),
        False,
    ),
    (
        'not match for attribute; itself is an attribute; missing attribute in subject',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[{'section': SubjectMatch('letter')}],
            resources=[Any()],
        ),
        Inquiry(subject={'digit': 'a'}, action={'section': 'a'}, resource='d'),
        False,
    ),
    (
        'not match for attribute; itself is an attribute; action is not a dict',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[{'section': SubjectMatch('letter')}],
            resources=[Any()],
        ),
        Inquiry(subject={'letter': 'b'}, action='b', resource='d'),
        False,
    ),
    (
        'match for attribute; itself is an attribute. several attrs and rules',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[{'section': SubjectMatch('letter'), 'method': ResourceMatch('ref_method')}],
            resources=[Any()],
        ),
        Inquiry(subject={'digit': 7, 'letter': 'a'},
                action={'section': 'a', 'method': 'get'},
                resource={'ref_method': 'get'}),
        True,
    ),
    (
        'match for value in context',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[Any()],
            resources=[Any()],
            context={'section': SubjectMatch()}
        ),
        Inquiry(subject='a', action='b', resource='c', context={'section': 'a'}),
        True,
    ),
    (
        'match for attribute in context',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[Any()],
            resources=[Any()],
            context={'section': SubjectMatch('letter')}
        ),
        Inquiry(subject={'letter': 'a'}, action='b', resource='c', context={'section': 'a'}),
        True,
    ),
    (
        'not match for attribute in context',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[Any()],
            resources=[Any()],
            context={'section': SubjectMatch('letter')}
        ),
        Inquiry(subject={'letter': 'a'}, action='b', resource='c', context={'section': 'X'}),
        False,
    ),
])
def test_is_allowed_for_inquiry_match_rules(desc, policy, inquiry, result):
    storage = MemoryStorage()
    storage.add(policy)
    g = Guard(storage, RulesChecker())
    assert result == g.is_allowed(inquiry), 'Failed for case: ' + desc


@pytest.mark.parametrize('inquiry, result, expect_message', [
    (
        Inquiry(subject='Max', action='watch', resource='TV'),
        True,
        "Incoming Inquiry was allowed. Inquiry: <class 'vakt.guard.Inquiry'> <Object ID some_ID>: " +
        "{'resource': 'TV', 'action': 'watch', 'subject': 'Max', 'context': {}}",
    ),
    (
        Inquiry(subject='Jim', action='watch', resource='TV'),
        False,
        "Incoming Inquiry was rejected. Inquiry: <class 'vakt.guard.Inquiry'> <Object ID some_ID>: " +
        "{'resource': 'TV', 'action': 'watch', 'subject': 'Jim', 'context': {}}",
    ),
])
def test_guard_logs_inquiry_decision(logger, inquiry, result, expect_message):
    # set up logging
    log_capture_str = io.StringIO()
    h = logging.StreamHandler(log_capture_str)
    h.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)
    logger.addHandler(h)
    # set up Guard
    storage = MemoryStorage()
    storage.add(Policy(
        uid='1',
        effect=ALLOW_ACCESS,
        subjects=['Max'],
        actions=['watch'],
        resources=['TV'],
    ))
    g = Guard(storage, RegexChecker())
    assert result == g.is_allowed(inquiry)
    log_res = log_capture_str.getvalue().strip()
    # a little hack to get rid of <Object ID 4502567760> in inquiry output
    log_res = re.sub(r'<Object ID \d+>', '<Object ID some_ID>', log_res)
    assert expect_message == log_res


def test_guard_does_not_fail_if_storage_returns_none(logger):
    class BadStorage(MemoryStorage):
        def find_for_inquiry(self, inquiry, checker=None):
            return None

    # set up logging
    log_capture_str = io.StringIO()
    h = logging.StreamHandler(log_capture_str)
    h.setLevel(logging.ERROR)
    logger.setLevel(logging.ERROR)
    logger.addHandler(h)
    # set up Guard
    storage = BadStorage()
    storage.add(Policy(
        uid='1',
        effect=ALLOW_ACCESS,
        subjects=['Max'],
        actions=['watch'],
        resources=['TV'],
    ))
    g = Guard(storage, RegexChecker())
    assert not g.is_allowed(Inquiry(subject='Max', action='watch', resource='TV'))
    assert 'Storage returned None, but is supposed to return at least an empty list' == \
           log_capture_str.getvalue().strip()
