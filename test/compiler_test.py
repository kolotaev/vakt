import pytest
from vakt.compiler import compile_regex
from vakt.exceptions import InvalidPattern


@pytest.mark.parametrize('phrase, start, end, output', [
    ('foo:bar:<.*>', '<', '>', '^foo\\:bar\\:(.*)$'),
    ('foo:bar:[.*]', '[', ']', '^foo\\:bar\\:(.*)$'),
    ('foo:bar:[фу-бар.*]', '[', ']', '^foo\\:bar\\:(фу-бар.*)$'),
    ('a', '{', '}', '^a$'),
    ('', '{', '}', '^$'),
    ('[[abc]+]', '[', ']', '^([abc]+)$'),
    ('foo:[[abc]+]:bar', '[', ']', '^foo\\:([abc]+)\\:bar$'),
    ('a:b:{foo-bar.*i{2}}', '{', '}', '^a\\:b\\:(foo-bar.*i{2})$'),
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
    with pytest.raises(InvalidPattern) as excinfo:
        compile_regex(phrase, start, end)
    assert phrase in str(excinfo.value)
    assert 'unbalanced braces' in str(excinfo.value)


@pytest.mark.parametrize('phrase, start, end, match_against, match_should_succeed', [
    ('foo:bar:<.*>', '<', '>', 'foo:bar:baz:me:python', True),
    ('foo:bar:<.*>', '<', '>', 'foo:bar:', True),
    ('foo:bar:<me*>', '<', '>', 'foo:bar:', False),
    ('foo.bar:<.*>', '<', '>', 'foo:bar:', False),
    ('foo:bar:<me*>', '<', '>', 'foo:bar:meeeeeeeeee', True),
    ('foo:bar:<me*>', '<', '>', 'foo:bar:m', True),
    ('[[abc]]', '[', ']', 'c', True),
    ('[.*]', '[', ']', '', True),
])
def test_compile_regex_output_matches_correctly(phrase, start, end, match_against, match_should_succeed):
    result = compile_regex(phrase, start, end)
    if match_should_succeed:
        assert result.match(match_against)
    else:
        assert result.match(match_against) is None
