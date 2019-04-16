import pytest

from vakt.parser import compile_regex
from vakt.exceptions import InvalidPatternError


@pytest.mark.parametrize('phrase, start, end, output', [
    ('foo-bar-<.*>', '<', '>', r'^foo\-bar\-(.*)$'),
    ('foo-bar-[.*]', '[', ']', r'^foo\-bar\-(.*)$'),
    ('foo-bar-[фу-бар.*]', '[', ']', r'^foo\-bar\-(фу-бар.*)$'),
    ('a', '{', '}', r'^a$'),
    ('', '{', '}', r'^$'),
    ('[]', '{', '}', r'^\[\]$'),
    ('a[{foo*}]b', '{', '}', r'^a\[(foo*)\]b$'),
    ('[[abc]+]', '[', ']', r'^([abc]+)$'),
    ('foo-[[abc]+]-bar', '[', ']', r'^foo\-([abc]+)\-bar$'),
    ('a-b-{foo-bar.*i{2}}', '{', '}', r'^a\-b\-(foo-bar.*i{2})$'),
])
def test_compile_regex_compiles_correctly(phrase, start, end, output):
    result = compile_regex(phrase, start, end)
    assert output == result.pattern


@pytest.mark.parametrize('phrase, start, end', [
    ('foo:bar:<.*', '<', '>'),
    (']', '[', ']'),
    ('ббб}', '{', '}'),
    ('№', '№', '№'),
    ('[yuy[]', '[', ']'),
    ('yuy[]]', '[', ']'),
    ('[ab[c[[v]]c]', '[', ']'),
])
def test_compile_regex_raises_exception_if_unbalanced(phrase, start, end):
    with pytest.raises(InvalidPatternError) as excinfo:
        compile_regex(phrase, start, end)
    assert phrase in str(excinfo.value)
    assert 'unbalanced braces' in str(excinfo.value)


@pytest.mark.parametrize('phrase, start, end, match_against, should_match_succeed', [
    ('foo:bar:<.*>', '<', '>', 'foo:bar:baz:me:python', True),
    ('foo:bar:<.*>', '<', '>', 'foo:bar:', True),
    ('foo.bar:<.*>', '<', '>', 'foo:bar:', False),
    ('foo:bar:<me*>', '<', '>', 'foo:bar:', False),
    ('foo:bar:<me*>', '<', '>', 'foo:bar:meeeeeeeeee', True),
    ('foo:bar:<me*>', '<', '>', 'foo:bar:m', True),
    ('[[abc]]', '[', ']', 'c', True),
    ('[.*]', '[', ']', '', True),
])
def test_compile_regex_output_matches_correctly(phrase, start, end, match_against, should_match_succeed):
    result = compile_regex(phrase, start, end)
    if should_match_succeed:
        assert result.match(match_against)
    else:
        assert not result.match(match_against)
