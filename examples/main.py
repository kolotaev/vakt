from vakt.matcher import RegexMatcher
from vakt.managers.memory import MemoryManager
from vakt.conditions.net import CIDRCondition
from vakt.conditions.request import SubjectEqualCondition
from vakt.effects import DENY_ACCESS, ALLOW_ACCESS
from vakt.policy import DefaultPolicy
from vakt.guard import Guard, Request


# First of all we need to create Policies for our online book library.
# They can be added at any time via PolicyManager.
# Here comes the list of Policies:
policies = [
    DefaultPolicy(
        id='1',
        description="""
        Allow all readers of the online library whose surnames start with M get and read
        """,
        effect=ALLOW_ACCESS,
        subjects=['<M[\w]+ >'],
        resources=('library:books:', 'office:printers', 'office:printers:<.+>'),
        actions=['<read|get>'],
        conditions={
            'ip': CIDRCondition('127.0.0.1/32'),
            'owner': SubjectEqualCondition(),
        },
    ),
    DefaultPolicy(
        id='2',
        description='Allow mr. Rooney and ms. Sparrow',
        effect=ALLOW_ACCESS,
        subjects=('Edward R. Rooney', 'Florence Sparrow'),
        actions=['update'],
        resources=['<.*>'],
        conditions={
            'ip': CIDRCondition('127.0.0.1/32'),
            'owner': SubjectEqualCondition(),
        },
    ),
    DefaultPolicy(
        id='3',
        description='Disallow Ferris Bueller to do anything inside library. Even to log-in',
        effect=DENY_ACCESS,
        subjects=['Ferris Bueller'],
        actions=['<.*>'],
        resources=['<.*>'],
    ),
]

# Here we instantiate the Policy Manager.
# In this case it's just in-memory one, but we can opt to SQL-storage Manager, MongoDB-storage Manager, etc.
pm = MemoryManager()


# Let's persist all our Policies so that to start serving our library.
for p in policies:
    pm.create(p)
