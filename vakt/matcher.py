import re

from .compiler import compile_regex
from .exceptions import InvalidPattern


# todo - move to policy class or as a trait?
class RegexMatcher:
    """Matcher that uses regular expressions."""

    def matches(self, policy, field, what):
        where = getattr(policy, field, [])
        for i in where:
            if policy.start_delimiter not in i:  # check if 'where' item is written in a policy-defined-regex syntax.
                if i == what:  # it's a single string match
                    return True
                continue
            try:
                pattern = compile_regex(i, policy.start_delimiter, policy.end_delimiter)
            except InvalidPattern as e:
                # todo - add logger
                # log here
                return False
            if re.match(pattern, what):
                return True
        return False


# todo - move to policy class or as a trait?
class StringMatcher:
    """Matcher that uses string equality."""

    def matches(self, policy, field, what):
        where = getattr(policy, field, [])
        for item in where:
            if policy.start_delimiter == item[0] and policy.end_delimiter == item[-1]:
                item = item[1:-1]
            if what == item:
                    return True
            continue
        return False
