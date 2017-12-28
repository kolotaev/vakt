import re

from compiler import compile_regex


# todo - move to policy class or as a trait?
class RegexMatcher:
    """
    Matcher that uses regular expressions.
    """

    @staticmethod
    def matches(policy, where, what):
        for i in where:
            if policy.start_delimiter not in i:
                # it's a single string match
                if i == what:
                    return True
                else:
                    continue

            pattern = compile_regex(i, policy.start_delimiter, policy.end_delimiter)
            if pattern:
                if re.match(pattern, what):
                    return True
                continue

            try:
                pattern = compile_regex(i, policy.start_delimiter, policy.end_delimiter)
            except ValueError as e:
                # todo - add logger
                # log here
                return False
            if re.match(pattern, what):
                return True

        return False
