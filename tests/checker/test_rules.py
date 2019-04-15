import pytest

from vakt.checker import RulesChecker
from vakt.policy import Policy
from vakt.rules.operator import *


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
        Policy(7.4, subjects=({}, {})),
        'subjects',
        {'name': 'Bob', 'stars': 890},
        False
    ),
    (
        Policy(8, subjects=[{'name': Eq('Max')}]),
        'subjects',
        {'name': 'Jimmy'},
        False
    ),
    (
        Policy(8.1, subjects=({'name': Eq('Max')},)),
        'subjects',
        {'name': 'Max'},
        True
    ),
    (
        Policy(9, subjects=[Eq('Max')]),
        'subjects',
        'Max',
        True
    ),
    (
        Policy(9.1, subjects=[Eq('Max'), Eq('Sally')]),
        'subjects',
        'Sally',
        True
    ),
    (
        Policy(9.2, subjects=[Eq('Max'), Eq('Sally'), Greater(50)]),
        'subjects',
        900,
        True
    ),
    (
        Policy(9.3, subjects=[Eq('Max'), Eq('Sally')]),
        'subjects',
        'Sam',
        False
    ),
    (
        Policy(10, subjects=[Eq('Max'), {'name': Eq('Sally')}]),
        'subjects',
        'Max',
        True
    ),
    (
        Policy(10.1, subjects=[Eq('Max'), {'name': Eq('Sally')}]),
        'subjects',
        'Bob',
        False
    ),
    (
        Policy(10.2, subjects=[Eq('Max'), {'name': Eq('Sally')}]),
        'subjects',
        {'name': 'Max'},
        False
    ),
    (
        Policy(10.3, subjects=[Eq('Max'), {'name': Eq('Sally')}]),
        'subjects',
        {'name': 'Sally'},
        True
    ),
    (
        Policy(10.4, subjects=[Eq('Max'), {'name': Eq('Sally')}]),
        'subjects',
        {'name': 'Bob'},
        False
    ),
    (
        Policy(10.5, subjects=[Eq('Max'), {'name': Eq('Sally')}]),
        'subjects',
        {'nick': 'Bob'},
        False
    ),
    (
        Policy(11, description='should cause exception str is not Rule', subjects=[{'nick': 'Bob'}]),
        'subjects',
        {'nick': 'Bob'},
        False
    ),
])
def test_fits(policy, field, what, result):
    c = RulesChecker()
    assert result == c.fits(policy, field, what)
