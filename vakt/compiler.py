from functools import lru_cache
import re
from vakt.exceptions import InvalidPattern

__all__ = ['compile_regex']


@lru_cache(maxsize=512)
def compile_regex(phrase, start_delimiter, end_delimiter):
    regex_vars = []
    pattern = '^'
    end = 0
    try:
        idxs = get_delimiter_indices(phrase, start_delimiter, end_delimiter)
    except InvalidPattern as e:
        raise e
    for i, idx in enumerate(idxs[::2]):
        raw = phrase[end:idx]
        end = idxs[i+1]
        pt = phrase[idx+1:end-1]
        pattern = pattern + "%s(%s)" % (re.escape(raw), pt)
        regex_vars.insert(i//2, re.compile('^%s$' % pt))
        raw = phrase[end:]
        pattern = '%s%s$' % (pattern, re.escape(raw))
        return re.compile(pattern)


def get_delimiter_indices(string, start, end):
    error_msg = "Pattern %s has unbalanced braces" % string
    idx, level = 0, 0
    idxs = []
    for i, s in enumerate(string):
        if s == start:
            level = level + 1
            if level == 1:
                idx = i
        elif s == end:
            level = level - 1
            if level == 0:
                idxs.append(idx)
                idxs.append(i + 1)
            elif level < 0:
                raise InvalidPattern(error_msg)

    if level != 0:
        raise InvalidPattern(error_msg)
    return idxs
