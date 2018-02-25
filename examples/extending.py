# This example shows how to extend Vakt functionality and use it in your code.

import vakt.conditions.base
import vakt.policy


class ABCondition(vakt.conditions.base.Condition):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def satisfied(self, what=None, request=None):
        return self.a == self.b


class CustomDelimitersPolicy(vakt.policy.DefaultPolicy):
    @property
    def start_delimiter(self):
        """Policy expression start tag"""
        return '@'

    @property
    def end_delimiter(self):
        """Policy expression end tag"""
        return '@'
