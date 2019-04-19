# This example shows how to extend Vakt functionality and use it in your code.

import vakt
from vakt.rules.base import Rule


class Between(Rule):
    def __init__(self, a, b, inclusive=False):
        self.a = a
        self.b = b
        self.inclusive = inclusive

    def satisfied(self, what, inquiry=None):
        return what > self.a and ((what < self.b and not self.inclusive) or (what <= self.b and self.inclusive))


class CustomTagsPolicy(vakt.Policy):
    @property
    def start_tag(self):
        """Policy expression start tag"""
        return '='

    @property
    def end_tag(self):
        """Policy expression end tag"""
        return '='


# You can use custom Rules in any Policy's context.
policy1 = CustomTagsPolicy(uid=1,
                           description='some custom policy',
                           subjects=('=[FGH]+[\w]+=', 'Max'),
                           context={'secret': Between(10, 100)})

policy2 = vakt.Policy(uid=2,
                      description='some default policy',
                      context={'secret': Between(1, 15)})


# You can add custom policies and default ones.
storage = vakt.MemoryStorage()
storage.add(policy1)
storage.add(policy2)


# You can use to_json() on custom and default policies.
data = list(map(lambda x: x.to_json(), storage.get_all(2, 0)))
print(data)

# You can use from_json() on custom and default policies.
data = list(map(vakt.policy.Policy.from_json, data))
print(data)
