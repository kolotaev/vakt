import pytest
from vakt.compiler import compile_regex


@pytest.mark.parametrize('phrase, start, end, output', [
    ('foo:bar:<.*>', '<', '>', '^foo\\:bar\\:(.*)$'),
    ('foo:bar:[.*]', '[', ']', '^foo\\:bar\\:(.*)$'),
    ('a', '{', '}', '^a$'),
    ('a:b:{foo-bar.*i{2}}', '{', '}', '^a\\:b\\:(foo-bar.*i{2})$')
])
def test_compile_regex_compiles_correctly(phrase, start, end, output):
    result = compile_regex(phrase, start, end)
    assert output == result.pattern
