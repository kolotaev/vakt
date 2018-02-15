import re
from functools import lru_cache

from .exceptions import InvalidPattern


__all__ = ['compile_regex']


@lru_cache(maxsize=1024)
def compile_regex(phrase, start_delimiter, end_delimiter):
    regex_vars = []
    pattern = '^'
    end = 0
    try:
        indices = get_delimiter_indices(phrase, start_delimiter, end_delimiter)
    except InvalidPattern as e:
        raise e
    for i, idx in enumerate(indices[::2]):
        raw = phrase[end:idx]
        end = indices[i+1]
        pt = phrase[idx+1:end-1]
        pattern = pattern + '%s(%s)' % (re.escape(raw), pt)
        regex_vars.insert(i//2, re.compile('^%s$' % pt))
    raw = phrase[end:]
    return re.compile('%s%s$' % (pattern, re.escape(raw)))


def get_delimiter_indices(string, start, end):
    error_msg = 'Pattern %s has unbalanced braces'
    idx, level = 0, 0
    indices = []
    for i, s in enumerate(string):
        if s == start:
            level = level + 1
            if level == 1:
                idx = i
        elif s == end:
            level = level - 1
            if level == 0:
                indices.append(idx)
                indices.append(i + 1)
            elif level < 0:
                raise InvalidPattern(error_msg % string)

    if level != 0:
        raise InvalidPattern(error_msg % string)
    return indices
