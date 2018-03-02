# This example shows how to extend Vakt functionality and use it in your code.

import vakt.conditions.base
import vakt.policy
import vakt.managers.memory


class ABCondition(vakt.conditions.base.Condition):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def satisfied(self, what, request=None):
        return self.a < what < self.b


class CustomDelimitersPolicy(vakt.policy.DefaultPolicy):
    @property
    def start_delimiter(self):
        """Policy expression start tag"""
        return '='

    @property
    def end_delimiter(self):
        """Policy expression end tag"""
        return '='


# You can use custom conditions in any policy.
policy1 = CustomDelimitersPolicy(1,
                                 description='some custom policy',
                                 subjects=('=[FGH]+[\w]+=', 'Max'),
                                 conditions={'secret': ABCondition(10, 100)})
policy2 = vakt.policy.DefaultPolicy(2,
                                    description='some default policy',
                                    conditions={'secret': ABCondition(1, 15)})


# You can add custom policies and default ones.
storage = vakt.managers.memory.MemoryManager()
storage.create(policy1)
storage.create(policy2)


# You can use to_json() on custom and default policies.
data = list(map(lambda x: x.to_json(), storage.get_all(1, 2)))
print(data)

# You can use from_json() on custom and default policies.
data = list(map(vakt.policy.DefaultPolicy.from_json, data))
print(data)
