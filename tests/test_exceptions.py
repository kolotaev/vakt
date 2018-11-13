import pytest

from vakt.exceptions import PolicyExistsError, UnknownCheckerType
from vakt.checker import RegexChecker


class MyChecker(RegexChecker):
    pass


@pytest.mark.parametrize('uid, message', [
    ('', 'Conflicting UID = '),
    ('123', 'Conflicting UID = 123'),
])
def test_poicy_exists_message(uid, message):
    ex = PolicyExistsError(uid)
    assert message == str(ex)


@pytest.mark.parametrize('obj, message', [
    (RegexChecker(), "Can't determine Checker type. Given: RegexChecker"),
    (MyChecker(), "Can't determine Checker type. Given: MyChecker"),
    (1, "Can't determine Checker type. Given: int"),
])
def test_unknown_checker_message(obj, message):
    ex = UnknownCheckerType(obj)
    assert message == str(ex)
