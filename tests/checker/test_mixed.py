import pytest

from vakt.checker import MixedChecker, RegexChecker, RulesChecker
from vakt.policy import Policy
from vakt.rules.operator import *


@pytest.mark.parametrize('checkers, policy, field, what, result', [
    (
        [],
        Policy(0, subjects=('baz', {'name': Eq('Max')}, '<bar.*>')),
        'subjects',
        {'name': 'Max'},
        False
    ),
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


def test_empty_init_args():
    with pytest.raises(TypeError) as excinfo:
        MixedChecker()
