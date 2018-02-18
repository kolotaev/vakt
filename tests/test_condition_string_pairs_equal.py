import pytest

from vakt.conditions.string import StringPairsEqualCondition


@pytest.mark.parametrize('against, result', [
    ([[]], False),
    ([], True),
    ("not-list", False),
    ([['a']], False),
    ([['a', 'a']], True),
    ([['й', 'й']], True),
    ([[1, '1']], False),
    ([['1', 1]], False),
    ([['a', 'b']], False),
    ([['a', 'b', 'c']], False),
    ([['a', 'a'], ['b', 'b']], True),
    ([['a', 'a'], ['b', 'c']], False),
])
def test_string_pairs_equal_satisfied(against, result):
    c = StringPairsEqualCondition()
    assert result == c.satisfied(against)
