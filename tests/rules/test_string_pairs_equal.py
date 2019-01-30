import pytest

from vakt.rules.string import PairsEqual, StringPairsEqualRule


@pytest.mark.parametrize('against, result', [
    ([[]], False),
    ([], True),
    ("not-list", False),
    ([['a']], False),
    ([['a', 'a']], True),
    ([['й', 'й']], True),
    ([[1, '1']], False),
    ([['1', 1]], False),
    ([[1, 1]], False),
    ([[1.0, 1.0]], False),
    ([['a', 'b']], False),
    ([['a', 'b', 'c']], False),
    ([['a', 'a'], ['b', 'b']], True),
    ([['a', 'a'], ['b', 'c']], False),
])
def test_string_pairs_equal_satisfied(against, result):
    c = PairsEqual()
    assert result == c.satisfied(against)
    # test after (de)serialization
    assert result == PairsEqual.from_json(PairsEqual().to_json()).satisfied(against)
    # test deprecated class
    with pytest.deprecated_call():
        c = StringPairsEqualRule()
        assert result == c.satisfied(against)
        assert result == StringPairsEqualRule.from_json(c.to_json()).satisfied(against)
