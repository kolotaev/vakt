from vakt.effects import ALLOW_ACCESS, DENY_ACCESS


def test_effects():
    assert 'allow' == ALLOW_ACCESS
    assert 'deny' == DENY_ACCESS
