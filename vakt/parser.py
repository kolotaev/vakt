import re

from .exceptions import InvalidPatternError


__all__ = ['compile_regex']


def compile_regex(phrase, start_tag, end_tag):
    """Compiles a string denoted by tags to a regular expression"""
    regex_vars, pattern, end = [], '', 0
    indices = get_tag_indices(phrase, start_tag, end_tag)
    for i, idx in enumerate(indices[::2]):
        raw = phrase[end:idx]
        end = indices[i+1]
        pt = phrase[idx+1:end-1]
        # todo - de we need escape?
        pattern = pattern + '%s(%s)' % (re.escape(raw), pt)
        regex_vars.insert(i//2, re.compile('^%s$' % pt))
    raw = phrase[end:]
    return re.compile('^%s%s$' % (pattern, re.escape(raw)))


def get_tag_indices(string, start, end):
    """
    Find and return list of tag indices in the given string.
    Raises exception if tags are not balanced (e.g. <<foo>)
    """
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
                raise InvalidPatternError(error_msg, string)

    if level != 0:
        raise InvalidPatternError(error_msg, string)
    return indices
