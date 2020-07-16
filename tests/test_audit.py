import logging
import io

from vakt.audit import (PoliciesUidMsg, PoliciesNopMsg,
                        PoliciesDescriptionMsg, PoliciesCountMsg)
from vakt.policy import Policy
from vakt.effects import ALLOW_ACCESS


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


def test_formatter():
    log_capture_string = io.StringIO()
    h = logging.StreamHandler(log_capture_string)
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter(
        '%(name)s - level: %(levelname)s - msg: %(message)s - effect: %(effect)s - pols: %(policies)s'
    ))
    audit_log = logging.getLogger('vakt.audit')
    audit_log.setLevel(logging.DEBUG)
    audit_log.addHandler(h)
    pmc = PoliciesUidMsg
    audit_log.info('Test', extra={'effect': ALLOW_ACCESS, 'policies': pmc([Policy(123), Policy('asdf')])})
    assert 'vakt.audit - level: INFO - msg: Test - effect: allow - pols: [123, asdf]\n' == \
           log_capture_string.getvalue()
