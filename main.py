from vakt.conditions.base import Condition


class ABCondition(Condition):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def satisfied(self, what=None, request=None):
        return self.a == self.b


d = ABCondition(8, 90).to_json()
print(d)

c = Condition.from_json(d)
print(c)
print(c.satisfied())
