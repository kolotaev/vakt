"""
All Rules simple operator comparisons:
==
!=
<
>
<=
>=
"""

import logging

from ..rules.base import Rule

log = logging.getLogger(__name__)


class Equal(Rule):
    """Rule that is satisfied when two values are equal '==' (type-aware comparison)"""
    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        return self.val == what


class NotEqual(Rule):
    """Rule that is satisfied when two values are not equal '!=' (type-aware comparison)"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        return self.val != what


class Greater(Rule):
    """Rule that is satisfied when 'what' is greater '>' than initial value"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        return self.val > what


class Less(Rule):
    """Rule that is satisfied when 'what' is less '<' than initial value"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        return self.val < what


class GreaterOrEqual(Rule):
    """Rule that is satisfied when 'what' is greater or equal '>=' than initial value"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        return self.val >= what


class LessOrEqual(Rule):
    """Rule that is satisfied when 'what' is less or equal '<=' than initial value"""

    def __init__(self, val):
        self.val = val

    def satisfied(self, what, inquiry=None):
        return self.val <= what
