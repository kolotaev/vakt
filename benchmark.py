import random
import uuid
import timeit
import sys

from vakt.storage.memory import MemoryStorage
from vakt.rules.net import CIDRRule
from vakt.effects import DENY_ACCESS, ALLOW_ACCESS
from vakt.policy import Policy
from vakt.checker import RegexChecker
from vakt.guard import Guard, Inquiry


# Grab number of policies in DB from the CLI argument
POLICIES_NUMBER = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
# Grab should Policies be defined without Regex syntax? from CLI argument
USE_REGEXP_POLICIES = False if len(sys.argv) > 2 and sys.argv[2] == 'no' else True


def rand_string():
    return ''.join([chr(random.randint(97, 122)) for _ in range(0, 10)])


def rand_true():
    return bool(random.getrandbits(1))


def gen_id():
    return str(uuid.uuid4())


store = MemoryStorage()

for x in range(POLICIES_NUMBER):
    if USE_REGEXP_POLICIES:
        subjects = ('<[\d]{3}[%s]*>' % rand_string(), '<[%s]{2}>' % rand_string())
    else:
        subjects = (rand_string(), rand_string())

    policy = Policy(
        id=gen_id(),
        effect=ALLOW_ACCESS if rand_true() else DENY_ACCESS,
        subjects=subjects,
        resources=('library:books:<.+>', 'office:magazines:<.+>'),
        actions=['<read|get>'],
        rules={
            'ip': CIDRRule('127.0.0.1'),
        },
    )
    store.add(policy)


guard = Guard(store, RegexChecker())

inq = Inquiry(action='get', subject='xo', resource='library:books:1234', context={'ip': '127.0.0.1'})


def single_inquiry_benchmark():
    if guard.is_allowed(inq):
        return True
    return False


if __name__ == '__main__':
    start = timeit.default_timer()
    allowed = single_inquiry_benchmark()
    stop = timeit.default_timer()
    print('Number of unique Policies in DB: {:,}'.format(POLICIES_NUMBER))
    print('Are Policies defined in Regex syntax?: %s' % USE_REGEXP_POLICIES)
    print('Single Inquiry decision took: %0.4f seconds' % (stop - start))
    print('Inquiry passed the guard? %s' % allowed)
