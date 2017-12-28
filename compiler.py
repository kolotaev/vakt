from functools import lru_cache
import re

__all__ = ['compile_regex']


@lru_cache(maxsize=512)
def compile_regex(phrase, start, end):
    regex_vars = []
    pattern = '^'
    try:
        idxs = get_delimiter_indices(phrase, start, end)
    except ValueError as e:
        raise e
    for i in idxs[::2]:
        raw = phrase[end:idxs[i]]
        end_i = idxs[i+1]
        pattern = phrase[idxs[i]+1:end-1]


def get_delimiter_indices(string, start, end):
    error_msg = "Pattern %s has unbalanced braces" % string
    idx, level = 0, 0
    idxs = []
    for i in string:
        if i == start:
            level = level + 1
            if level == 1:
                idx = i
        elif i == end:
            level = level - 1
            if level == 0:
                idxs.append(idx)
                idxs.append(i + 1)
            elif level < 0:
                raise ValueError(error_msg)
    if level != 0:
        raise ValueError(error_msg)
    return idxs
