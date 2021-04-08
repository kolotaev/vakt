import random
import uuid
import timeit
import argparse
import contextlib
import threading
import statistics
from functools import partial

from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from redis import Redis

from vakt import (
    MemoryStorage, DENY_ACCESS, ALLOW_ACCESS,
    Policy, RegexChecker, StringExactChecker, StringFuzzyChecker, RulesChecker, Guard, Inquiry,
)
from vakt.storage.mongo import MongoStorage
from vakt.storage.sql import SQLStorage
from vakt.storage.sql.migrations import SQLMigrationSet
from vakt.storage.redis import RedisStorage, JSONSerializer, PickleSerializer
from vakt.rules import operator, logic, list, net


# Globals
LINE_LEN = 80
overall_policies_created = 0
similar_regexp_policies_created = 0


# Define and parse possible arguments
parser = argparse.ArgumentParser(description='Run vakt benchmark.')
parser.add_argument('-n', '--number', dest='policies_number', nargs='?', type=int, default=100000,
                    help='number of policies to create in DB (default: %(default)d)')
parser.add_argument('-s', '--storage', choices=('mongo', 'memory', 'sql', 'redis'), default='memory',
                    help='type of storage (default: %(default)s)')
parser.add_argument('-d', '--dsn', dest='sql_dsn', nargs='?', type=str, default='sqlite:///:memory:',
                    help='DSN connection string for sql storage (default: %(default)s)')
parser.add_argument('-c', '--checker', choices=('regex', 'rules', 'exact', 'fuzzy'), default='regex',
                    help='type of checker (default: %(default)s)')
parser.add_argument('-t', '--threads', nargs='?', type=int, default=1,
                    help='number of concurrent requests (default: %(default)s)')

regex_group = parser.add_argument_group('regex policy related')
regex_group.add_argument('--regexp', action='store_false', default=True,
                         help='should Policies be defined without Regex syntax? (default: %(default)s)')
regex_group.add_argument('--same', type=int, default=0,
                         help='number of similar regexps in Policy')
regex_group.add_argument('--cache', type=int,
                         help="number of LRU-cache for RegexChecker (default: RegexChecker's default cache-size)")

redis_group = parser.add_argument_group('Redis Storage related')
redis_group.add_argument('--serializer', choices=('json', 'pickle'), default='json',
                         help='type of serializer for policies stored in Redis (default: %(default)s)')

ARGS = parser.parse_args()


def rand_string():
    return ''.join([chr(random.randint(97, 122)) for _ in range(0, 10)])


def rand_true():
    return bool(random.getrandbits(1))


def gen_id():
    return str(uuid.uuid4())


def gen_regexp():
    a, b = [rand_string() for _ in range(2)]
    return r'<[\d]{3}[%s]*>' % a, '<[%s]{2}>' % b


def gen_policy():
    if ARGS.checker == 'rules':
        return Policy(
            uid=gen_id(),
            effect=ALLOW_ACCESS if rand_true() else DENY_ACCESS,
            subjects=[
                {
                    'name': logic.Or(operator.Eq('Nicky'), operator.Eq('Nick')),
                    'stars': logic.And(
                        operator.Greater(random.randint(-1000, -1)),
                        operator.Less(random.randint(1000, 3000)),
                        operator.Eq(900)
                    ),
                    'status': operator.Eq('registered')
                },
            ],
            resources=(
                {
                    'method': list.AnyIn('get', 'post', 'delete'),
                    'path': list.NotIn('org/custom', 'vacations/pending', 'должность/повысить'),
                    'id': operator.Eq(rand_string())
                },
                {
                    'method': operator.Eq('violate'),
                }
            ),
            actions=(
                {'before': operator.Eq('foo')},
                {'after': list.In(rand_string(), rand_string(), rand_string())},
            ),
            context={
                'ip': net.CIDR('127.0.0.1'),
            },
        )
    else:
        global similar_regexp_policies_created
        static_subjects = gen_regexp()
        if ARGS.regexp:
            if similar_regexp_policies_created < ARGS.same:
                subjects = static_subjects
                similar_regexp_policies_created += 1
            else:
                subjects = gen_regexp()
        else:
            subjects = (rand_string(), rand_string())
        return Policy(
            uid=gen_id(),
            effect=ALLOW_ACCESS if rand_true() else DENY_ACCESS,
            subjects=subjects,
            resources=('library:books:<.+>', 'office:magazines:<.+>'),
            actions=['<' + rand_string() + '|' + rand_string() + '>'],
            context={
                'ip': net.CIDR('127.0.0.1'),
            },
        )


def get_checker():
    if ARGS.checker == 'rules':
        return RulesChecker()
    elif ARGS.checker == 'exact':
        return StringExactChecker()
    elif ARGS.checker == 'fuzzy':
        return StringFuzzyChecker()
    return RegexChecker(ARGS.cache) if ARGS.cache else RegexChecker()


def get_inquiry():
    if ARGS.checker == 'rules':
        return Inquiry(
            subject={'name': 'Nick', 'stars': 900, 'status': 'registered'},
            resource={'method': ['post', 'get'], 'path': '/acme/users', 'id': rand_string()},
            action={'before': 'foo', 'after': rand_string()},
            context={'ip': '127.0.0.1'}
        )
    return Inquiry(action='get', subject='xo', resource='library:books:1234', context={'ip': '127.0.0.1'})


def populate_storage(store):
    global overall_policies_created
    for x in range(ARGS.policies_number):
        policy = gen_policy()
        store.add(policy)
        overall_policies_created += 1
        yield


def print_generation(generator, factor=10, line_len=LINE_LEN):
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
    elif ARGS.storage == 'sql':
        engine = create_engine(ARGS.sql_dsn)
        sql_session = scoped_session(sessionmaker(bind=engine))
        storage = SQLStorage(scoped_session=sql_session)
        migration = SQLMigrationSet(storage)
        migration.up()
        yield storage
        # todo - why is there left an uncommitted transaction?
        sql_session.commit()
        migration.down()
    if ARGS.storage == 'redis':
        collection = 'vakt_policies_benchmark'
        client = Redis('127.0.0.1', 6379, db=0)
        if ARGS.serializer == 'json':
            serializer = JSONSerializer()
        elif ARGS.serializer == 'pickle':
            serializer = PickleSerializer()
        else:
            serializer = None
        yield RedisStorage(client, collection=collection, serializer=serializer)
        client.flushdb()
        client.close()
    else:
        yield MemoryStorage()


if __name__ == '__main__':
    with get_storage() as st:
        allowed = []
        threads = []
        call_time_results = []
        checker = get_checker()
        guard = Guard(st, checker)
        def check_allow(guard, inquiry, allowed, call_time_results):
            start = timeit.default_timer()
            a = guard.is_allowed(inquiry=inquiry)
            stop = timeit.default_timer()
            allowed.append(a)
            call_time_results.append(stop - start)
        print('=' * LINE_LEN)
        print('Populating %s with Policies' % st.__class__.__name__)
        print_generation(partial(populate_storage, st), int(ARGS.policies_number / 100 * 1), LINE_LEN)
        print('START BENCHMARK!')
        for _ in range(ARGS.threads):
            t = threading.Thread(target=check_allow, args=(guard, get_inquiry(), allowed, call_time_results))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        # fix for statistics - we need at least 2 datapoints
        if len(call_time_results) == 1:
            call_time_results.append(call_time_results[0])
        # reports:
        print('Number of unique Policies in DB: {:,}'.format(overall_policies_created))
        print('Among them Policies with the same regexp pattern: {:,}'.format(similar_regexp_policies_created))
        print('Checker used: %s' % checker.__class__.__name__)
        print('Storage used: %s' % st.__class__.__name__)
        print('Number of concurrent threads: {:,}'.format(ARGS.threads))
        print('Decision for Inquiry took (mean: %0.4f seconds. stdev: %0.4f)' %
            (statistics.mean(call_time_results), statistics.stdev(call_time_results)))
        print('Inquiry passed the guard? %s' % allowed[0])
        print('=' * LINE_LEN)
