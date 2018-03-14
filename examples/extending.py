# This example shows how to extend Vakt functionality and use it in your code.

import vakt.rules.base
import vakt.policy
import vakt.storage.memory


class ABRule(vakt.rules.base.Rule):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def satisfied(self, what, inquiry=None):
        return self.a < what < self.b


class CustomTagsPolicy(vakt.policy.Policy):
    @property
    def start_tag(self):
        """Policy expression start tag"""
        return '='

    @property
    def end_tag(self):
        """Policy expression end tag"""
        return '='


# You can use custom rules in any policy.
policy1 = CustomTagsPolicy(1,
                                 description='some custom policy',
                                 subjects=('=[FGH]+[\w]+=', 'Max'),
                                 rules={'secret': ABRule(10, 100)})
policy2 = vakt.policy.Policy(2,
                                    description='some default policy',
                                    rules={'secret': ABRule(1, 15)})


# You can add custom policies and default ones.
storage = vakt.storage.memory.MemoryStorage()
storage.add(policy1)
storage.add(policy2)


# You can use to_json() on custom and default policies.
data = list(map(lambda x: x.to_json(), storage.get_all(2, 0)))
print(data)

# You can use from_json() on custom and default policies.
data = list(map(vakt.policy.Policy.from_json, data))
print(data)
