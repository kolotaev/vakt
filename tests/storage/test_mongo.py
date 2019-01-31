import uuid
import random
import types

import pytest
from pymongo import MongoClient
from bson.objectid import ObjectId

from vakt.storage.mongo import *
from vakt.policy import Policy
from vakt.rules.string import Equal
from vakt.exceptions import PolicyExistsError, UnknownCheckerType
from vakt.guard import Inquiry
from vakt.checker import StringExactChecker, StringFuzzyChecker, RegexChecker


MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
DB_NAME = 'vakt_db'
COLLECTION = 'vakt_policies'


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
            st.add(st.add(Policy(id, description='bar')))

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
        (500, 0, 200),
        (101, 1, 101),
        (500, 50, 150),
        (200, 0, 200),
        (200, 1, 199),
        (199, 0, 199),
        (200, 50, 150),
        (0, 0, 200),
        (1, 0, 1),
        (5, 4, 5),
    ])
    def test_get_all(self, st, limit, offset, result):
        for i in range(200):
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

    @pytest.mark.parametrize('checker', [
        None,
        RegexChecker(256),
    ])
    def test_find_for_inquiry_with_regex_or_none_checker_specified_return_all_existing_policies(self, st, checker):
        st.add(Policy('1', subjects=['max', 'bob']))
        st.add(Policy('2', subjects=['sam', 'foo']))
        st.add(Policy('3', subjects=['bar']))
        inquiry = Inquiry(subject='Jim', action='delete', resource='server')
        found = st.find_for_inquiry(inquiry, checker)
        found = list(found)
        assert 3 == len(found)

    def test_find_for_inquiry_with_exact_string_checker(self, st):
        st.add(Policy('1', subjects=['max', 'bob'], actions=['get'], resources=['books', 'comics', 'magazines']))
        st.add(Policy('2', subjects=['maxim'], actions=['get'], resources=['books', 'comics', 'magazines']))
        st.add(Policy('3', subjects=['sam', 'nina']))
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

    def test_find_for_inquiry_with_unknown_checker(self, st):
        st.add(Policy('1'))
        inquiry = Inquiry(subject='sam', action='get', resource='books')
        with pytest.raises(UnknownCheckerType):
            list(st.find_for_inquiry(inquiry, Inquiry()))

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
