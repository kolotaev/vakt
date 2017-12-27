from functools import lru_cache

class Matcher:
    """

    """

    @lru_cache(512)
    def matches(self, policy, where, what):
