import vakt


def test_types():
    assert 1 == vakt.TYPE_STRING_BASED
    assert 2 == vakt.TYPE_RULE_BASED


def test_version():
    assert '1.2.0' == vakt.__version__


def test_version_info():
    assert (1, 2, 0) == vakt.version_info()
