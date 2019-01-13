import pytest

from vakt.rules.net import CIDRRule


@pytest.mark.parametrize('cidr, ip, result', [
    ('192.168.2.0/24', '192.168.2.56', True),
    ('192.168.2.0/28', '192.168.2.56', False),
    ('2', '192.168.2.56', False),
    ('192.168.2.0/28', '2', False),
    ('0.0.0.0/0', '192.168.2.56', True),
])
def test_cidr_satisfied(cidr, ip, result):
    c = CIDRRule(cidr)
    assert result == c.satisfied(ip)
    assert result == CIDRRule.from_json(c.to_json()).satisfied(ip)
