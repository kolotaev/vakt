import logging
import io
import sys
import re

import pytest

from vakt.audit import (PoliciesUidMsg, PoliciesNopMsg,
                        PoliciesDescriptionMsg, PoliciesCountMsg)
from vakt.policy import Policy, PolicyAllow, PolicyDeny
from vakt.effects import ALLOW_ACCESS
from vakt.guard import Guard, Inquiry
from vakt.checker import RegexChecker
from vakt.storage.memory import MemoryStorage


@pytest.fixture()
def audit_log():
    al = logging.getLogger('vakt.audit')
    initial_handlers = al.handlers[:]
    initial_level = al.getEffectiveLevel()
    yield al
    al.handlers = initial_handlers
    al.setLevel(initial_level)


def test_policies_nop_msg():
    p1 = Policy(123, description='foo', actions=['books:<foo.bar>'],
                resources=['bb'], subjects=['<qwerty>'], context={})
    p2 = Policy('asdf', description='bar', actions=['books:<foo.bar>'],
                resources=['aa'], subjects=['<qwerty>'], context={})
    m = PoliciesNopMsg([p1, p2])
    assert '' == str(m)
    m = PoliciesNopMsg([p2])
    assert '' == str(m)
    m = PoliciesNopMsg()
    assert '' == str(m)


def test_policies_uid_msg():
    p1 = Policy(123, description='foo', actions=['books:<foo.bar>'],
                resources=['bb'], subjects=['<qwerty>'], context={})
    p2 = Policy('asdf', description='bar', actions=['books:<foo.bar>'],
                resources=['aa'], subjects=['<qwerty>'], context={})
    m = PoliciesUidMsg([p1, p2])
    assert '[123, asdf]' == str(m)
    m = PoliciesUidMsg([p2])
    assert '[asdf]' == str(m)
    m = PoliciesUidMsg()
    assert '[]' == str(m)


def test_policies_description_msg():
    p1 = Policy(123, description='foo', actions=['books:<foo.bar>'],
                resources=['bb'], subjects=['<qwerty>'], context={})
    p2 = Policy('asdf', description='bar', actions=['books:<foo.bar>'],
                resources=['aa'], subjects=['<qwerty>'], context={})
    m = PoliciesDescriptionMsg([p1, p2])
    assert "['foo', 'bar']" == str(m)
    m = PoliciesDescriptionMsg([p2])
    assert "['bar']" == str(m)
    m = PoliciesDescriptionMsg()
    assert '[]' == str(m)


def test_policies_count_msg():
    p1 = Policy(123, description='foo', actions=['books:<foo.bar>'],
                resources=['bb'], subjects=['<qwerty>'], context={})
    p2 = Policy('asdf', description='bar', actions=['books:<foo.bar>'],
                resources=['aa'], subjects=['<qwerty>'], context={})
    m = PoliciesCountMsg([p1, p2])
    assert 'count = 2' == str(m)
    m = PoliciesCountMsg([p2])
    assert 'count = 1' == str(m)
    m = PoliciesCountMsg()
    assert 'count = 0' == str(m)


def test_formatter_usage(audit_log):
    log_capture_str = io.StringIO()
    h = logging.StreamHandler(log_capture_str)
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter(
        '%(name)s - level: %(levelname)s - msg: %(message)s - effect: %(effect)s - pols: %(candidates)s'
    ))
    audit_log.setLevel(logging.DEBUG)
    audit_log.addHandler(h)
    pmc = PoliciesUidMsg
    audit_log.info('Test', extra={'effect': ALLOW_ACCESS, 'candidates': pmc([Policy(123), Policy('asdf')])})
    assert 'vakt.audit - level: INFO - msg: Test - effect: allow - pols: [123, asdf]' == \
           log_capture_str.getvalue().strip()


def test_guard_logs_messages_at_info_level(audit_log):
    log_capture_str = io.StringIO()
    h = logging.StreamHandler(log_capture_str)
    h.setLevel(logging.INFO)
    audit_log.setLevel(logging.INFO)
    audit_log.addHandler(h)
    g = Guard(MemoryStorage(), RegexChecker())
    g.is_allowed(Inquiry())
    assert 'No potential' in log_capture_str.getvalue().strip()


def test_guard_does_not_log_messages_at_more_than_info_level(audit_log):
    log_capture_str = io.StringIO()
    h = logging.StreamHandler(log_capture_str)
    h.setLevel(logging.WARN)
    audit_log.setLevel(logging.WARN)
    audit_log.addHandler(h)
    g = Guard(MemoryStorage(), RegexChecker())
    g.is_allowed(Inquiry())
    assert '' == log_capture_str.getvalue().strip()


@pytest.mark.parametrize('inquiry, is_allowed, expect_msg', [
    (
        Inquiry(action='get', subject='Max', resource='book'),
        True,
        'msg: All matching policies have allow effect | ' +
        'effect: allow | ' +
        'deciders: [a, b] | ' +
        'candidates: [a, b] | ' +
        "inquiry: <class 'vakt.guard.Inquiry'> <Object ID some_ID>: " +
        "{'resource': 'book', 'action': 'get', 'subject': 'Max', 'context': {}}",
    ),
    (
        Inquiry(action='update', subject='Max', resource='book'),
        True,
        'msg: All matching policies have allow effect | ' +
        'effect: allow | ' +
        'deciders: [a] | ' +
        'candidates: [a] | ' +
        "inquiry: <class 'vakt.guard.Inquiry'> <Object ID some_ID>: " +
        "{'resource': 'book', 'action': 'update', 'subject': 'Max', 'context': {}}",
    ),
    (
        Inquiry(),
        False,
        'msg: No potential policies were found | ' +
        'effect: deny | ' +
        'deciders: [] | ' +
        'candidates: [] | ' +
        "inquiry: <class 'vakt.guard.Inquiry'> <Object ID some_ID>: " +
        "{'resource': '', 'action': '', 'subject': '', 'context': {}}",
    ),
    (
        Inquiry(action='watch', subject='Jim', resource='book', context={'stars': 129}),
        False,
        'msg: One of matching policies has deny effect | ' +
        'effect: deny | ' +
        'deciders: [d] | ' +
        'candidates: [c, d] | ' +
        "inquiry: <class 'vakt.guard.Inquiry'> <Object ID some_ID>: " +
        "{'resource': 'book', 'action': 'watch', 'subject': 'Jim', 'context': {'stars': 129}}",
    ),
])
def test_guard_uses_audit_correctly(audit_log, inquiry, is_allowed, expect_msg):
    # setup logger consumer
    log_capture_str = io.StringIO()
    h = logging.StreamHandler(log_capture_str)
    h.setFormatter(logging.Formatter(
        'msg: %(message)s | effect: %(effect)s | deciders: %(deciders)s | candidates: %(candidates)s | ' +
        'inquiry: %(inquiry)s'
    ))
    h.setLevel(logging.INFO)
    audit_log.setLevel(logging.INFO)
    audit_log.addHandler(h)
    # setup guard
    st = MemoryStorage()
    st.add(PolicyAllow(uid='a', subjects=['Max'], actions=['<.*>'], resources=['<.*>']))
    st.add(PolicyAllow(uid='b', subjects=['Max'], actions=['get'], resources=['<.*>']))
    st.add(PolicyAllow(uid='c', subjects=['Jim'], actions=['<.*>'], resources=['<.*>']))
    st.add(PolicyDeny(uid='d', subjects=['Jim'], actions=['<.*>'], resources=['<.*>']))
    st.add(PolicyAllow(uid='e'))
    g = Guard(st, RegexChecker())
    # Run tests
    assert is_allowed == g.is_allowed(inquiry)
    result = log_capture_str.getvalue().strip()
    # a little hack to get rid of <Object ID 4502567760> in inquiry output
    result = re.sub(r'<Object ID \d+>', '<Object ID some_ID>', result)
    assert expect_msg == result


def test_guard_can_use_specific_policies_message_class(audit_log):
    # setup logger consumer
    log_capture_str = io.StringIO()
    h = logging.StreamHandler(log_capture_str)
    h.setFormatter(logging.Formatter('decs: %(deciders)s, candidates: %(candidates)s'))
    h.setLevel(logging.INFO)
    audit_log.setLevel(logging.INFO)
    audit_log.addHandler(h)
    # setup guard
    st = MemoryStorage()
    st.add(PolicyAllow('122'))
    st.add(PolicyAllow('123', actions=['<.*>'], resources=['<.*>'], subjects=['<.*>']))
    st.add(PolicyDeny('124', actions=['<.*>'], resources=['<.*>'], subjects=['<.*>']))
    st.add(PolicyDeny('125', actions=['<.*>'], resources=['<.*>'], subjects=['<.*>']))
    g = Guard(st, RegexChecker(), audit_policies_cls=PoliciesCountMsg)
    # Run tests
    g.is_allowed(Inquiry(action='get', subject='Kim', resource='TV'))
    assert 'decs: count = 1, candidates: count = 3' == log_capture_str.getvalue().strip()
