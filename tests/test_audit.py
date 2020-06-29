import logging
import io

from vakt.audit import policies_message_class
from vakt.policy import Policy
from vakt.effects import ALLOW_ACCESS


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
    pmc = policies_message_class()
    audit_log.info('Test', extra={'effect': ALLOW_ACCESS, 'policies': pmc([Policy(123), Policy('asdf')])})
    assert 'vakt.audit - level: INFO - msg: Test - effect: allow - pols: [123,asdf]\n' == \
           log_capture_string.getvalue()
