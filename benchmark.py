import random
import uuid
import timeit
import sys

from vakt.storage.memory import MemoryStorage
from vakt.rules.net import CIDR
from vakt.effects import DENY_ACCESS, ALLOW_ACCESS
from vakt.policy import Policy
from vakt.checker import RegexChecker
from vakt.guard import Guard, Inquiry


# Grab number of policies in DB from the CLI argument
POLICIES_NUMBER = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
# Grab should Policies be defined without Regex syntax? from CLI argument
USE_REGEXP_POLICIES = False if len(sys.argv) > 2 and sys.argv[2] == 'no' else True
# Grab number of similar regexps in policy
SAME_REGEX_POLICIES_NUMBER = int(sys.argv[3]) if len(sys.argv) > 3 else 0
# Grab number of LRU-cache for RegexChecker
CACHE_SIZE = int(sys.argv[4]) if len(sys.argv) > 4 else None


def rand_string():
    return ''.join([chr(random.randint(97, 122)) for _ in range(0, 10)])


def rand_true():
    return bool(random.getrandbits(1))


def gen_id():
    return str(uuid.uuid4())


def gen_regexp():
    a, b = [rand_string() for _ in range(2)]
    return '<[\d]{3}[%s]*>' % a, '<[%s]{2}>' % b


def populate_storage():
    global store, overall_policies_created, similar_regexp_policies_created
    static_subjects = gen_regexp()

    for x in range(POLICIES_NUMBER):
        if USE_REGEXP_POLICIES:
            if similar_regexp_policies_created < SAME_REGEX_POLICIES_NUMBER:
                subjects = static_subjects
                similar_regexp_policies_created += 1
            else:
                subjects = gen_regexp()
        else:
            subjects = (rand_string(), rand_string())

        policy = Policy(
            uid=gen_id(),
            effect=ALLOW_ACCESS if rand_true() else DENY_ACCESS,
            subjects=subjects,
            resources=('library:books:<.+>', 'office:magazines:<.+>'),
            actions=['<read|get>'],
            context={
                'ip': CIDR('127.0.0.1'),
            },
        )
        store.add(policy)
        overall_policies_created += 1
        yield


def print_generation(generator, factor=10, line_len=80):
    cl, cf = 0, 0
    for _ in generator():
        if cf < factor:
            cf += 1
            continue
        print('.', end='', flush=True)
        cl += 1
        cf = 0
        if cl >= line_len:
            cl = 0
            print()
    print()


def single_inquiry_benchmark():
    global guard
    if guard.is_allowed(inq):
        return True
    return False


overall_policies_created = 0
similar_regexp_policies_created = 0
store = MemoryStorage()
checker = RegexChecker(CACHE_SIZE) if CACHE_SIZE else RegexChecker()
guard = Guard(store, checker)
inq = Inquiry(action='get', subject='xo', resource='library:books:1234', context={'ip': '127.0.0.1'})


if __name__ == '__main__':
    line_length = 80
    print('=' * line_length)
    print('Populating MemoryStorage with Policies')
    print_generation(populate_storage, int(POLICIES_NUMBER / 100 * 1), line_length)
    print('START BENCHMARK!')
    start = timeit.default_timer()
    allowed = single_inquiry_benchmark()
    stop = timeit.default_timer()
    print('Number of unique Policies in DB: {:,}'.format(overall_policies_created))
    print('Among them there are Policies with the same regexp pattern: {:,}'.format(similar_regexp_policies_created))
    print('Are Policies defined in Regexp syntax?: %s' % USE_REGEXP_POLICIES)
    print('Decision for 1 Inquiry took: %0.4f seconds' % (stop - start))
    print('Inquiry passed the guard? %s' % allowed)
    print('=' * line_length)
