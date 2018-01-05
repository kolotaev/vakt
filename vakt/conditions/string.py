from vakt.conditions.base import Condition


class StringEqualCondition(Condition):
    """Condition that is fulfilled if the string value equals the specified property of this condition"""

    def __init__(self, equals):
        if not isinstance(equals, str):
            raise TypeError('equals  property should be a string')
        self.equals = equals

    def fulfills(self, what, request):
        return isinstance(what, str) and what == self.equals


class StringPairsEqualCondition(Condition):
    pass
