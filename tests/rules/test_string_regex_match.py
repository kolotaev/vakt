import pytest

from vakt.rules.string import RegexMatch, RegexMatchRule
from vakt.rules.base import Rule


def test_regex_match_construct_fails():
    with pytest.raises(TypeError) as excinfo:
        RegexMatch('[lll')
    assert 'pattern should be a valid regexp string' in str(excinfo.value)
    assert 'unterminated character set at position 0' in str(excinfo.value) \
           or 'unexpected end of regular expression' in str(excinfo.value)


@pytest.mark.parametrize('arg, against, result', [
    ('.*', 'foo', True),
    ('aaa', 'aaa', True),
    ('aaa', 'aab', False),
    (r'[\d\w]+', '567asd', True),
    ('', '', True),
    (r'^python\?exe$', 'python?exe', True),
    (r'^python?exe$', 'python?exe', False),
])
def test_regex_match_rule_satisfied(arg, against, result):
    c = RegexMatch(arg)
    assert result == c.satisfied(against)
    # test after (de)serialization
    js = RegexMatch(arg).to_json()
    assert result == Rule.from_json(js).satisfied(against)
    # test deprecated class
    with pytest.deprecated_call():
        c = RegexMatchRule(arg)
        assert result == c.satisfied(against)
        assert result == RegexMatchRule.from_json(c.to_json()).satisfied(against)
