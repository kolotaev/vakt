import logging
import io

import pytest

from vakt.audit import (PoliciesUidMsg, PoliciesNopMsg,
                        PoliciesDescriptionMsg, PoliciesCountMsg)
from vakt.policy import Policy, PolicyAllow
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
        '%(name)s - level: %(levelname)s - msg: %(message)s - effect: %(effect)s - pols: %(policies)s'
    ))
    audit_log.setLevel(logging.DEBUG)
    audit_log.addHandler(h)
    pmc = PoliciesUidMsg
    audit_log.info('Test', extra={'effect': ALLOW_ACCESS, 'policies': pmc([Policy(123), Policy('asdf')])})
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
    assert 'Denied' in log_capture_str.getvalue().strip()


def test_guard_does_not_log_messages_at_more_than_info_level(audit_log):
    log_capture_str = io.StringIO()
    h = logging.StreamHandler(log_capture_str)
    h.setLevel(logging.WARN)
    audit_log.setLevel(logging.WARN)
    audit_log.addHandler(h)
    g = Guard(MemoryStorage(), RegexChecker())
    g.is_allowed(Inquiry())
    assert '' == log_capture_str.getvalue().strip()


@pytest.mark.xfail(reason='todo')
def test_guard_uses_audit_correctly(audit_log):
    # setup logger consumer
    log_capture_str = io.StringIO()
    h = logging.StreamHandler(log_capture_str)
    h.setLevel(logging.INFO)
    audit_log.setLevel(logging.INFO)
    audit_log.addHandler(h)
    # setup guard
    st = MemoryStorage()
    policies = [
        PolicyAllow(
            uid='55',
            subjects=['Max'],
            actions=['update'],
            resources=['<.*>'],
        ),
        PolicyAllow(
            uid='56',
            subjects=['Max'],
            actions=['get'],
            resources=['<.*>'],
        ),
        PolicyAllow(
            uid='57'
        ),
    ]
    for p in policies:
        st.add(p)
    g = Guard(st, RegexChecker())
    # Run tests
    assert g.is_allowed(Inquiry(action='get', subject='Max', resource='book'))
    assert 'Allowed: all matching policies have allow effect' == log_capture_str.getvalue().strip()


@pytest.mark.xfail(reason='todo')
def test_guard_can_use_specific_policies_message_class():
    pass
