import pytest

from vakt.checker import RegexChecker, RulesChecker
from vakt.storage.memory import MemoryStorage
from vakt.rules.operator import Eq, NotEq, Greater
from vakt.rules.logic import Any
from vakt.effects import DENY_ACCESS, ALLOW_ACCESS
from vakt.policy import Policy
from vakt.guard import Guard, Inquiry


@pytest.mark.parametrize('desc, policy, inquiry, checker, should_be_allowed', [
    (
        'RegexChecker: Should not match since actions and resources are not specified',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=['foo'],
        ),
        Inquiry(subject='foo'),
        RegexChecker(),
        False,
    ),
    (
        'RulesChecker: Should not match since actions and resources are not specified',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[{'name': Eq('Sally')}],
        ),
        Inquiry(subject={'name': 'Sally'}),
        RulesChecker(),
        False,
    ),
    (
        'RulesChecker: Should not match since resources are not specified',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[{'name': Eq('Sally')}],
            actions=[{'action': Eq('GET')}],
        ),
        Inquiry(subject={'name': 'Sally'}, action={'action': 'GET'}),
        RulesChecker(),
        False,
    ),
    (
        'RulesChecker: Should match since everything matches',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[{'name': Eq('Sally')}],
            actions=[{'action': NotEq('POST')}],
            resources=[{'endpoint': Eq('/metrics/cpu')}]
        ),
        Inquiry(subject={'name': 'Sally'}, action={'action': 'GET'}, resource={'endpoint': '/metrics/cpu'}),
        RulesChecker(),
        True,
    ),
    (
        'RulesChecker: Should match since everything matches by Any condition',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Any()],
            actions=[Any()],
            resources=[Eq('/metrics/cpu'), Eq('/metrics/mem')]
        ),
        Inquiry(subject='Sally', action='GET', resource='/metrics/cpu'),
        RulesChecker(),
        True,
    ),
    (
        'RulesChecker: Should match because of user\'s stars and correct book',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Eq('Admin'), {'stars': Greater(50)}],
            actions=[Any()],
            resources=[{'book': Eq('Potter')}, {'magzine': Any()}]
        ),
        Inquiry(subject={'stars': 870}, action='GET', resource={'book': 'Potter'}),
        RulesChecker(),
        True,
    ),
    (
        'RulesChecker: Should match because of any magazine and Admin user',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Eq('Admin'), {'stars': Greater(50)}],
            actions=[Any()],
            resources=[{'book': Eq('Potter')}, {'magzine': Any()}]
        ),
        Inquiry(subject='Admin', action='POST', resource={'magzine': 'asdfghjkl'}),
        RulesChecker(),
        True,
    ),
    (
        'RulesChecker: Should not match because of wrong user',
        Policy(
            uid=1,
            effect=ALLOW_ACCESS,
            subjects=[Eq('Admin'), {'stars': Greater(50)}],
            actions=[Any()],
            resources=[{'book': Eq('Potter')}, {'magzine': Any()}]
        ),
        Inquiry(subject={'stars': 2}, action='READ', resource={'magzine': 'asdfghjkl'}),
        RulesChecker(),
        False,
    ),
])
def test_policy_inquiry_checker_examples(desc, policy, inquiry, checker, should_be_allowed):
    storage = MemoryStorage()
    storage.add(policy)
    g = Guard(storage, checker)
    assert should_be_allowed == g.is_allowed(inquiry)
