from functools import lru_cache
import re


@lru_cache(maxsize=512)
def compile_regex(phrase, start, end):
    return re.compile(phrase)
