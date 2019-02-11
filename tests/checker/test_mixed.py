import pytest

from vakt.checker import MixedChecker, RegexChecker, RulesChecker
from vakt.policy import Policy
from vakt.rules.operator import *


@pytest.mark.parametrize('checkers, policy, field, what, result', [
    (
        [RegexChecker()],
        Policy(1, subjects=('baz', {'name': Eq('Max')}, '<bar.*>')),
        'subjects',
        'baz',
        True
    ),
    (
        [RulesChecker()],
        Policy(2, subjects=('baz', {'name': Eq('Max')}, '<bar.*>')),
        'subjects',
        'foo',
        False
    ),
    (
        [RulesChecker(), RegexChecker()],
        Policy(3, subjects=('baz', {'name': Eq('Max')}, '<bar.*>')),
        'subjects',
        'foo',
        False
    ),
    (
        [RulesChecker(), RegexChecker()],
        Policy(4, subjects=('baz', {'name': Eq('Max')}, '<foo.*>')),
        'subjects',
        'foo',
        True
    ),
    (
        [RulesChecker(), RegexChecker()],
        Policy(5, subjects=('baz', {'name': Eq('Max')}, '<foo.*>')),
        'subjects',
        {'name': 'Max'},
        True
    ),
])
def test_fits(checkers, policy, field, what, result):
    c = MixedChecker(*checkers)
    assert result == c.fits(policy, field, what)


@pytest.mark.parametrize('checkers, exception, msg', [
    ([], TypeError, 'Mixed Checker must be comprised of at least one Checker'),
    (
        [RegexChecker],
        TypeError,
        "Mixed Checker can only be comprised of other Checkers, but <class 'abc.ABCMeta'> given"
    ),
    (
        [RegexChecker(), RulesChecker],
        TypeError,
        "Mixed Checker can only be comprised of other Checkers, but <class 'abc.ABCMeta'> given"
    ),
])
def test_bad_init_args(checkers, exception, msg):
    with pytest.raises(exception) as excinfo:
        MixedChecker(*checkers)
    assert msg in str(excinfo.value)
