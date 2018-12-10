import vakt


def test_types():
    assert 1 == vakt.TYPE_STRINGS
    assert 2 == vakt.TYPE_ATTRIBUTES


def test_version():
    assert '1.1.0' == vakt.__version__
