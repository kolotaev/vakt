import vakt
from vakt import __version__


def test_version():
    assert '1.2.1' == __version__


def test_version_info():
    assert (1, 2, 1) == vakt.version_info()
