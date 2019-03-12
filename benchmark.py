import random
import uuid
import timeit
import argparse
import contextlib

from pymongo import MongoClient

from vakt.storage.memory import MemoryStorage
from vakt.storage.mongo import MongoStorage
from vakt.rules.net import CIDR
from vakt.effects import DENY_ACCESS, ALLOW_ACCESS
from vakt.policy import Policy
from vakt.checker import RegexChecker
from vakt.guard import Guard, Inquiry


# Define and parse possible arguments
parser = argparse.ArgumentParser(description='Run vakt benchmark.')
parser.add_argument('policies_number', nargs='?', type=int, default=100000,
                    help='number of policies to create in DB (default: %(default)s)')
parser.add_argument('--storage', choices=('mongo', 'memory'), default='memory',
                    help='type of storage (default: %(default)s)')

regex_group = parser.add_argument_group('regex policy related')
regex_group.add_argument('--regexp', action='store_false', default=True,
                         help='should Policies be defined without Regex syntax? (default: %(default)s)')
regex_group.add_argument('--same', type=int, default=0,
                         help='number of similar regexps in Policy')
regex_group.add_argument('--cache', type=int,
                         help="number of LRU-cache for RegexChecker (default: RegexChecker's default cache-size)")

ARGS = parser.parse_args()


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

    for x in range(ARGS.policies_number):
        if ARGS.regexp:
            if similar_regexp_policies_created < ARGS.same:
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


@contextlib.contextmanager
def get_storage():
    if ARGS.storage == 'mongo':
        db_name = 'vakt_db'
        collection = 'vakt_policies_benchmark'
        client = MongoClient('127.0.0.1', 27017)
        yield MongoStorage(client, db_name, collection=collection)
        client[db_name][collection].delete_many({})
        client.close()
    else:
        yield MemoryStorage()


store = None
overall_policies_created = 0
similar_regexp_policies_created = 0
checker = RegexChecker(ARGS.cache) if ARGS.cache else RegexChecker()
inq = Inquiry(action='get', subject='xo', resource='library:books:1234', context={'ip': '127.0.0.1'})


if __name__ == '__main__':
    with get_storage() as st:
        store = st
        line_length = 80
        print('=' * line_length)
        print('Populating MemoryStorage with Policies')
        print_generation(populate_storage, int(ARGS.policies_number / 100 * 1), line_length)
        print('START BENCHMARK!')
        start = timeit.default_timer()
        allowed = Guard(store, checker).is_allowed(inq)
        stop = timeit.default_timer()
        print('Number of unique Policies in DB: {:,}'.format(overall_policies_created))
        print('Among them Policies with the same regexp pattern: {:,}'.format(similar_regexp_policies_created))
        print('Are Policies defined in Regexp syntax?: %s' % ARGS.regexp)
        print('Decision for 1 Inquiry took: %0.4f seconds' % (stop - start))
        print('Inquiry passed the guard? %s' % allowed)
        print('=' * line_length)
