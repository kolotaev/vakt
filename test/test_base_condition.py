from vakt.conditions.base import Condition


class ABCondition(Condition):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def satisfied(self, what=None, request=None):
        return self.a == self.b


def test_to_json():
    conditions = [
        ABCondition(1, 2),
        ABCondition('x', 'y'),
    ]
    assert '{"type": "test_base_condition.ABCondition", "contents": {"a": 1, "b": 2}}' == conditions[0].to_json()
    assert '{"type": "test_base_condition.ABCondition", "contents": {"a": "x", "b": "y"}}' == conditions[1].to_json()


def test_from_json():
    conditions = [
        '{"type": "test_base_condition.ABCondition", "contents": {"a": 1, "b": 1}}',
        '{"type": "test_base_condition.ABCondition", "contents": {"a": "x", "b": "y"}}',
    ]
    c1 = Condition.from_json(conditions[0])
    c2 = Condition.from_json(conditions[1])
    assert isinstance(c1, ABCondition)
    assert isinstance(c2, ABCondition)
    assert c1.satisfied()
    assert not c2.satisfied()


def test_name():
    assert 'test_base_condition.ABCondition' == ABCondition(1, 2).name()


def test_satisfied():
    assert ABCondition(2, 2).satisfied()
    assert not ABCondition(1, 2).satisfied()

