import pytest

from vakt.checker import RulesChecker
from vakt.policy import Policy
from vakt.rules.logic import *


@pytest.mark.parametrize('policy, field, what, result', [
    (
        Policy(0, subjects=()),
        'subjects',
        {'name': 'Max'},
        False
    ),
    (
        Policy(1, subjects=({'name': Eq('Max')},)),
        'subjects',
        {'name': 'Max'},
        True
    ),
    (
        Policy(2, subjects=[{'name': Eq('Max')}]),
        'subjects',
        {'name': 'John'},
        False
    ),
    (
        Policy(3, subjects=({'name': Eq('Max')}, {'stars': Greater(50)})),
        'subjects',
        {'name': 'Max'},
        True
    ),
    (
        Policy(3.1, subjects=({'name': Eq('Max')}, {'stars': Greater(50)})),
        'subjects',
        {'stars': 799},
        True
    ),
    (
        Policy(3.2, subjects=({'name': Eq('Max')}, {'stars': Greater(50)})),
        'subjects',
        {'name': 'James'},
        False
    ),
    (
        Policy(3.3, subjects=({'name': Eq('Max')}, {'stars': Greater(50)})),
        'subjects',
        {'stars': 9},
        False
    ),
    (
        Policy(4, subjects=[{'name': Eq('Max')}, {'stars': Greater(50)}]),
        'subjects',
        {'name': 'Max', 'stars': 700},
        True
    ),
    (
        Policy(4.1, subjects=[{'name': Eq('Max')}, {'stars': Greater(50)}]),
        'subjects',
        {'name': 'Sonny', 'stars': 700},
        True
    ),
    (
        Policy(4.11, subjects=[{'name': Eq('Max')}, {'stars': Greater(50)}]),
        'subjects',
        {'name': 'Sonny', 'stars': 8},
        False
    ),
    (
        Policy(4.2, subjects=[{'name': Eq('Max')}, {'stars': Greater(50)}]),
        'subjects',
        {'name': 'Max', 'stars': 51},
        True
    ),
    (
        Policy(4.21, subjects=[{'name': Eq('Max')}, {'stars': Greater(50)}]),
        'subjects',
        {'name': 'Sonny', 'stars': 0},
        False
    ),
    (
        Policy(5, subjects=({'name': Eq('Max'), 'stars': Greater(50)}, {'name': Eq('Jim'), 'stars': Greater(10)})),
        'subjects',
        {'stars': 11, 'name': 'Jim'},
        True
    ),
    (
        Policy(6, subjects=({'name': Eq('Max'), 'stars': Greater(50)}, {'name': Eq('Jim'), 'stars': Greater(10)})),
        'subjects',
        {'stars': 9, 'name': 'Jim'},
        False
    ),
    (
        Policy(7, subjects=({'name': Eq('Max'), 'stars': Greater(50)}, {})),
        'subjects',
        {'stars': 440, 'name': 'Max'},
        True
    ),
    (
        Policy(7.1, subjects=({'name': Eq('Max'), 'stars': Greater(50)}, {})),
        'subjects',
        {'stars': 2, 'name': 'Max'},
        False
    ),
    (
        Policy(7.2, subjects=({}, {})),
        'subjects',
        {'stars': 2, 'name': 'Max'},
        False
    ),
    (
        Policy(7.3, subjects=({}, {})),
        'subjects',
        {},
        False
    ),
    (
        Policy(8, subjects=('baz', {'name': Eq('Max')}, '<bar.*>')),
        'subjects',
        {'name': 'Jimmy'},
        False
    ),
    (
        Policy(8.1, subjects=('baz', {'name': Eq('Max')}, '<bar.*>')),
        'subjects',
        {'name': 'Max'},
        True
    ),
])
def test_fits(policy, field, what, result):
    c = RulesChecker()
    assert result == c.fits(policy, field, what)
