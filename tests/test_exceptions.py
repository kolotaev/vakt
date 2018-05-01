import pytest

from vakt.exceptions import PolicyExistsError


@pytest.mark.parametrize('uid, message', [
    ('', 'Conflicting ID = '),
    ('123', 'Conflicting ID = 123'),
])
def test_poicy_exists_message(uid, message):
    ex = PolicyExistsError(uid)
    assert message == str(ex)
