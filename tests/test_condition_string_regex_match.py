import pytest

from vakt.conditions.string import RegexMatchCondition


def test_regex_match_construct_fails():
    with pytest.raises(TypeError) as excinfo:
        RegexMatchCondition('[lll')
    assert 'pattern should be a valid regexp string' in str(excinfo.value)
    assert 'unterminated character set at position 0' in str(excinfo.value)


@pytest.mark.parametrize('arg, against, result', [
    ('.*', 'foo', True),
    ('aaa', 'aaa', True),
    ('aaa', 'aab', False),
    ('[\d\w]+', '567asd', True),
    ('', '', True),
    ('^python\?exe$', 'python?exe', True),
    ('^python?exe$', 'python?exe', False),
])
def test_regex_match_condition_satisfied(arg, against, result):
    c = RegexMatchCondition(arg)
    assert result == c.satisfied(against)
