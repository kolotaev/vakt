import uuid
import random
import types
import operator
import os
import unittest
from operator import attrgetter

import pytest
from pymongo import MongoClient
from bson.objectid import ObjectId

from vakt.storage.mongo import *
from vakt.storage.memory import MemoryStorage
from vakt.effects import ALLOW_ACCESS
from vakt.policy import Policy
from vakt.rules.string import Equal
from vakt.rules.logic import Any
from vakt.rules.operator import Eq
from vakt.exceptions import PolicyExistsError, UnknownCheckerType
from vakt.guard import Inquiry, Guard
from vakt.checker import StringExactChecker, StringFuzzyChecker, RegexChecker, RulesChecker


MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
DB_NAME = os.getenv('MONGO_DB_NAME', 'vakt_db_test')
COLLECTION = 'vakt_policies_test'
MIGRATION_COLLECTION = 'vakt_policies_migration_ver_test'


def create_client():
    return MongoClient(MONGO_HOST, MONGO_PORT)


@pytest.mark.integration
class TestMongoStorage:

    @pytest.fixture()
    def st(self):
        client = create_client()
        yield MongoStorage(client, DB_NAME, collection=COLLECTION)
        client[DB_NAME][COLLECTION].delete_many({})
        client.close()

    def test_add(self, st):
        id = str(uuid.uuid4())
        p = Policy(
            uid=id,
            description='foo bar баз',
            subjects=('Edward Rooney', 'Florence Sparrow'),
            actions=['<.*>'],
            resources=['<.*>'],
            context={
                'secret': Equal('i-am-a-teacher'),
            },
        )
        st.add(p)
        back = st.get(id)
        assert id == back.uid
        assert 'foo bar баз' == back.description
        assert isinstance(back.context['secret'], Equal)
        st.add(Policy('2', actions=[Eq('get'), Eq('put')], subjects=[Any()], resources=[{'books': Eq('Harry')}]))
        assert '2' == st.get('2').uid
        assert 2 == len(st.get('2').actions)
        assert 1 == len(st.get('2').subjects)
        assert isinstance(st.get('2').subjects[0], Any)
        assert 1 == len(st.get('2').resources)
        assert isinstance(st.get('2').resources[0]['books'], Eq)
        assert 'Harry' == st.get('2').resources[0]['books'].val

    def test_add_with_bson_object_id(self, st):
        id = str(ObjectId())
        p = Policy(
            uid=id,
            description='foo',
        )
        st.add(p)

        back = st.get(id)
        assert id == back.uid

    def test_policy_create_existing(self, st):
        id = str(uuid.uuid4())
        st.add(Policy(id, description='foo'))
        with pytest.raises(PolicyExistsError):
            st.add(Policy(id, description='bar'))

    def test_get(self, st):
        st.add(Policy('1'))
        st.add(Policy(2, description='some text'))
        assert isinstance(st.get('1'), Policy)
        assert '1' == st.get('1').uid
        assert 2 == st.get(2).uid
        assert 'some text' == st.get(2).description

    def test_get_nonexistent(self, st):
        assert None is st.get(123456789)

    @pytest.mark.parametrize('limit, offset, result', [
        (50, 0, 20),
        (11, 1, 11),
        (50, 5, 15),
        (20, 0, 20),
        (20, 1, 19),
        (19, 0, 19),
        (20, 5, 15),
        (0, 0, 0),
        (0, 10, 0),
        (1, 0, 1),
        (5, 4, 5),
    ])
    def test_get_all(self, st, limit, offset, result):
        for i in range(20):
            desc = ''.join(random.choice('abcde') for _ in range(30))
            st.add(Policy(str(i), description=desc))
        policies = list(st.get_all(limit=limit, offset=offset))
        assert result == len(policies)

    def test_get_all_check_policy_properties(self, st):
        p = Policy(
            uid='1',
            description='foo bar баз',
            subjects=('Edward Rooney', 'Florence Sparrow'),
            actions=['<.*>'],
            resources=['<.*>'],
            context={
                'secret': Equal('i-am-a-teacher'),
            },
        )
        st.add(p)
        policies = list(st.get_all(100, 0))
        assert 1 == len(policies)
        assert '1' == policies[0].uid
        assert 'foo bar баз' == policies[0].description
        assert ['Edward Rooney', 'Florence Sparrow'] == policies[0].subjects
        assert ['<.*>'] == policies[0].actions
        assert ['<.*>'] == policies[0].resources
        assert isinstance(policies[0].context['secret'], Equal)

    def test_get_all_with_incorrect_args(self, st):
        for i in range(10):
            st.add(Policy(str(i), description='foo'))
        with pytest.raises(ValueError) as e:
            list(st.get_all(-1, 9))
        assert "Limit can't be negative" == str(e.value)
        with pytest.raises(ValueError) as e:
            list(st.get_all(0, -3))
        assert "Offset can't be negative" == str(e.value)

    def test_get_all_returns_generator(self, st):
        st.add(Policy('1'))
        st.add(Policy('2'))
        found = st.get_all(500, 0)
        assert isinstance(found, types.GeneratorType)
        l = []
        for p in found:
            l.append(p.uid)
        assert 2 == len(l)

    def test_get_all_ascending_sorting_order(self, st):
        for i in range(1, 20):
            st.add(Policy(i))
        assert list(range(1, 20)) == list(map(attrgetter('uid'), st.get_all(30, 0)))

    @pytest.mark.parametrize('checker, expect_number', [
        (None, 6),
        (RegexChecker(), 2),
        (RulesChecker(), 2),
        (StringExactChecker(), 1),
        (StringFuzzyChecker(), 1),
    ])
    def test_find_for_inquiry_returns_existing_policies(self, st, checker, expect_number):
        st.add(Policy('1', subjects=['<[mM]ax>', '<.*>']))
        st.add(Policy('2', subjects=['sam<.*>', 'foo']))
        st.add(Policy('3', subjects=['Jim'], actions=['delete'], resources=['server']))
        st.add(Policy('3.1', subjects=['Jim'], actions=[r'del<\w+>'], resources=['server']))
        st.add(Policy('4', subjects=[{'stars': Eq(90)}, Eq('Max')]))
        st.add(Policy('5', subjects=[Eq('Jim'), Eq('Nina')]))
        inquiry = Inquiry(subject='Jim', action='delete', resource='server')
        found = st.find_for_inquiry(inquiry, checker)
        assert expect_number == len(list(found))

    def test_find_for_inquiry_with_exact_string_checker(self, st):
        st.add(Policy('1', subjects=['max', 'bob'], actions=['get'], resources=['books', 'comics', 'magazines']))
        st.add(Policy('2', subjects=['maxim'], actions=['get'], resources=['books', 'comics', 'magazines']))
        st.add(Policy('3', subjects=['sam', 'nina']))
        st.add(Policy('4', subjects=[Eq('sam'), Eq('nina')]))
        inquiry = Inquiry(subject='max', action='get', resource='books')
        found = st.find_for_inquiry(inquiry, StringExactChecker())
        found = list(found)
        assert 1 == len(found)
        assert '1' == found[0].uid

    def test_find_for_inquiry_with_fuzzy_string_checker(self, st):
        st.add(Policy('1', subjects=['max', 'bob'], actions=['get'], resources=['books', 'comics', 'magazines']))
        st.add(Policy('2', subjects=['maxim'], actions=['get'], resources=['books', 'foos']))
        st.add(Policy('3', subjects=['Max'], actions=['get'], resources=['books', 'comics']))
        st.add(Policy('4', subjects=['sam', 'nina']))
        st.add(Policy('5', subjects=[Eq('sam'), Eq('nina')]))
        inquiry = Inquiry(subject='max', action='et', resource='oo')
        found = st.find_for_inquiry(inquiry, StringFuzzyChecker())
        found = list(found)
        assert 2 == len(found)
        ids = [found[0].uid, found[1].uid]
        assert '1' in ids
        assert '2' in ids
        inquiry = Inquiry(subject='Max', action='get', resource='comics')
        found = st.find_for_inquiry(inquiry, StringFuzzyChecker())
        found = list(found)
        assert 1 == len(found)
        assert '3' == found[0].uid

    @pytest.mark.parametrize('policies, inquiry, expected_reference', [
        (
            [
                Policy(
                    uid=1,
                    actions=['get', 'post'],
                    effect=ALLOW_ACCESS,
                    resources=['<.*>'],
                    subjects=['<[Mm]ax>', '<Jim>']
                ),
            ],
            Inquiry(action='get', resource='printer', subject='Max'),
            True,
        ),
        (
            [
                Policy(
                    uid=1,
                    actions=['<.*>'],
                    effect=ALLOW_ACCESS,
                    resources=['<.*>'],
                    subjects=['<.*>']
                ),
            ],
            Inquiry(action='get', resource='printer', subject='Max'),
            True,
        ),
        (
            [
                Policy(
                    uid=1,
                    actions=['<.*>'],
                    effect=ALLOW_ACCESS,
                    resources=['library:books:<.+>'],
                    subjects=['<.*>']
                ),
            ],
            Inquiry(action='get', resource='library:books:dracula', subject='Max'),
            True,
        ),
        (
            [
                Policy(
                    uid=1,
                    actions=[r'<\d+>'],
                    effect=ALLOW_ACCESS,
                    resources=[r'<\w{1,3}>'],
                    subjects=[r'<\w{2}-\d+>']
                ),
            ],
            Inquiry(action='12', resource='Pie', subject='Jo-1'),
            True,
        ),
        (
            [
                Policy(
                    uid=1,
                    actions=['parse'],
                    effect=ALLOW_ACCESS,
                    resources=['library:books'],
                    subjects=['Max']
                ),
            ],
            Inquiry(action='parse', resource='library:books', subject='Max'),
            True,
        ),
        (
            [
                Policy(
                    uid=1,
                    actions=['parse'],
                    effect=ALLOW_ACCESS,
                    resources=['library:manu<(al|scripts)>'],
                    subjects=['Max']
                ),
            ],
            Inquiry(action='parse', resource='library:books', subject='Max'),
            False,
        ),
        (
            [
                Policy(
                    uid=1,
                    actions=['parse'],
                    effect=ALLOW_ACCESS,
                    resources=['library:books'],
                    subjects=['Max']
                ),
                Policy(
                    uid=2,
                    actions=['parse'],
                    effect=ALLOW_ACCESS,
                    resources=['library:manu<(al|scripts)>'],
                    subjects=['Max']
                ),
            ],
            Inquiry(action='parse', resource='library:manuscripts', subject='Max'),
            True,
        ),
    ])
    def test_find_for_inquiry_with_regex_checker(self, st, policies, inquiry, expected_reference):
        mem_storage = MemoryStorage()  # it returns all stored policies so we consider Guard as a reference
        for p in policies:
            st.add(p)
            mem_storage.add(p)
        reference_answer = Guard(mem_storage, RegexChecker()).is_allowed(inquiry)
        assert expected_reference == reference_answer, 'Check reference answer'
        assert reference_answer == Guard(st, RegexChecker()).is_allowed(inquiry), \
            'Mongo storage should give the same answers as reference'

    def test_find_for_inquiry_with_regex_checker_for_mongodb_prior_to_4_2(self, st):
        # mock db server version for this test
        st.db_server_version = (3, 4, 0)
        st.add(Policy('1', subjects=['<[mM]ax>', '<.*>']))
        st.add(Policy('2', subjects=['sam<.*>', 'foo']))
        st.add(Policy('3', subjects=['Jim'], actions=['delete'], resources=['server']))
        st.add(Policy('3.1', subjects=['Jim'], actions=[r'del<\w+>'], resources=['server']))
        st.add(Policy('4', subjects=[{'stars': Eq(90)}, Eq('Max')]))
        st.add(Policy('5', subjects=[Eq('Jim'), Eq('Nina')]))
        inquiry = Inquiry(subject='Jim', action='delete', resource='server')
        found = st.find_for_inquiry(inquiry, RegexChecker())
        found = list(found)
        # should return all string-based polices, but not only matched ones
        assert 4 == len(found)
        assert ['1', '2', '3', '3.1'] == sorted(map(attrgetter('uid'), found))

    def test_find_for_inquiry_with_rules_checker(self, st):
        assertions = unittest.TestCase('__init__')
        st.add(Policy(1, subjects=[{'name': Equal('Max')}], actions=[{'foo': Equal('bar')}]))
        st.add(Policy(2, subjects=[{'name': Equal('Max')}], actions=[{'foo': Equal('bar2')}]))
        st.add(Policy(3, subjects=['sam', 'nina']))
        st.add(Policy(4, actions=[r'<\d+>'], effect=ALLOW_ACCESS, resources=[r'<\w{1,3}>'], subjects=[r'<\w{2}-\d+>']))
        st.add(Policy(5, subjects=[{'name': Equal('Jim')}], actions=[{'foo': Equal('bar3')}]))
        inquiry = Inquiry(subject={'name': 'max'}, action='get', resource='books')
        found = st.find_for_inquiry(inquiry, RulesChecker())
        found = list(found)
        assert 3 == len(found)
        assertions.assertListEqual([1, 2, 5], list(map(operator.attrgetter('uid'), found)))

    def test_find_for_inquiry_with_unknown_checker(self, st):
        st.add(Policy('1'))
        inquiry = Inquiry(subject='sam', action='get', resource='books')
        with pytest.raises(UnknownCheckerType):
            list(st.find_for_inquiry(inquiry, Inquiry()))

    def test_find_for_inquiry_returns_generator(self, st):
        st.add(Policy('1', subjects=['max', 'bob'], actions=['get'], resources=['comics']))
        st.add(Policy('2', subjects=['max', 'bob'], actions=['get'], resources=['comics']))
        inquiry = Inquiry(subject='max', action='get', resource='comics')
        found = st.find_for_inquiry(inquiry)
        assert isinstance(found, types.GeneratorType)
        l = []
        for p in found:
            l.append(p.uid)
        assert 2 == len(l)

    def test_update(self, st):
        id = str(uuid.uuid4())
        policy = Policy(id)
        st.add(policy)
        assert id == st.get(id).uid
        assert None is st.get(id).description
        assert [] == st.get(id).actions
        policy.description = 'foo'
        policy.actions = ['a', 'b', 'c']
        st.update(policy)
        assert id == st.get(id).uid
        assert 'foo' == st.get(id).description
        assert ['a', 'b', 'c'] == st.get(id).actions
        p = Policy(2, actions=[Any()], subjects=[Eq('max'), Eq('bob')])
        st.add(p)
        assert 2 == st.get(2).uid
        p.actions = [Eq('get')]
        st.update(p)
        assert 1 == len(st.get(2).actions)
        assert 'get' == st.get(2).actions[0].val

    def test_update_non_existing_does_not_create_anything(self, st):
        id = str(uuid.uuid4())
        st.update(Policy(id, actions=['get'], description='bar'))
        assert st.get(id) is None

    def test_delete(self, st):
        policy = Policy('1')
        st.add(policy)
        assert '1' == st.get('1').uid
        st.delete('1')
        assert None is st.get('1')

    def test_delete_nonexistent(self, st):
        uid = str(ObjectId())
        st.delete(uid)
        assert None is st.get(uid)

    def test_returned_condition(self, st):
        uid = str(uuid.uuid4())
        p = Policy(
            uid=uid,
            context={
                'secret': Equal('i-am-a-teacher'),
                'secret2': Equal('i-am-a-husband'),

            },
        )
        st.add(p)
        context = st.get(uid).context
        assert context['secret'].satisfied('i-am-a-teacher')
        assert context['secret2'].satisfied('i-am-a-husband')
