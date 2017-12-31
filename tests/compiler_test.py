import pytest

from vakt.compiler import compile_regex


@pytest.mark.parametrize('phrase, start, end, output', [
    ('uri:foo:{.*}', '{', '}', 'op')
])
def test_compile_regex(phrase, start, end, output):
    assert output == compile_regex(phrase, start, end)
