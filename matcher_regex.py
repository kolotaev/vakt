from functools import lru_cache
import re

from compiler import regex


class RegexMatcher:
    """
    Matcher that uses regular expressions.
    """

    @staticmethod
    def matches(policy, where, what):

        # we have LRU cache instead of a standard simple re.compile builtin one.
        @lru_cache(maxsize=512)
        def get(phrase):
            return re.compile(phrase)

        for i in where:
            if policy.start_delimiter not in i:
                # it's a single string match
                if i == what:
                    return True
                else:
                    continue

            pattern = get(i)
            if pattern:
                if re.match(pattern, what):
                    return True
                continue

            try:
                pattern = regex.compile_regex(i, policy.start_delimiter, policy.end_delimiter)
            except ValueError as e:
                # todo - add logger
                # log here
                return False
            if re.match(pattern, what):
                return True

        return False
