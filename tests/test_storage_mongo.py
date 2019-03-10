import uuid
import random
import types
import json
import re
import unittest

import pytest
from pymongo import MongoClient
from bson.objectid import ObjectId

from vakt.storage.mongo import *
from vakt.storage.memory import MemoryStorage
from vakt.policy import Policy
from vakt.rules.string import StringEqualRule
from vakt.rules.base import Rule
from vakt.exceptions import PolicyExistsError, UnknownCheckerType
from vakt.guard import Inquiry, Guard
from vakt.effects import *
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
        client[DB_NAME][COLLECTION].remove()
        client.close()

    def test_add(self, st):
        id = str(uuid.uuid4())
        p = Policy(
            uid=id,
            description='foo bar баз',
            subjects=('Edward Rooney', 'Florence Sparrow'),
            actions=['<.*>'],
            resources=['<.*>'],
            rules={
                'secret': StringEqualRule('i-am-a-teacher'),
            },
        )
        st.add(p)
        back = st.get(id)
        assert id == back.uid
        assert 'foo bar баз' == back.description
        assert isinstance(back.rules['secret'], StringEqualRule)

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
            rules={
                'secret': StringEqualRule('i-am-a-teacher'),
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
        assert isinstance(policies[0].rules['secret'], StringEqualRule)

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
            rules={
                'secret': StringEqualRule('i-am-a-teacher'),
                'secret2': StringEqualRule('i-am-a-husband'),

            },
        )
        st.add(p)
        rules = st.get(uid).rules
        assert rules['secret'].satisfied('i-am-a-teacher')
        assert rules['secret2'].satisfied('i-am-a-husband')


@pytest.mark.integration
class TestMigration0To1x0x3:

    @pytest.fixture()
    def migration(self):
        client = create_client()
        storage = MongoStorage(client, DB_NAME, collection=COLLECTION)
        yield Migration0To1x1x0(storage)
        client[DB_NAME][COLLECTION].remove()
        client.close()

    def test_order(self, migration):
        assert 1 == migration.order

    def test_has_access_to_storage(self, migration):
        assert hasattr(migration, 'storage') and migration.storage is not None

    def test_up(self, migration):
        migration.up()
        created_indices = [i['name'] for i in migration.storage.collection.list_indexes()]
        assert created_indices == ['_id_', 'actions_idx', 'subjects_idx', 'resources_idx']

    def test_down(self, migration):
        migration.down()
        left_indices = [i['name'] for i in migration.storage.collection.list_indexes()]
        assert left_indices == ['_id_']


# Custom classes for TestMigration1x1x0To1x1x1
class WithObject(Rule):  # pragma: no cover
    def __init__(self, val):
        self.val = re.compile(val)

    def satisfied(self, what=None, inquiry=None):
        return True


class Simple(Rule):   # pragma: no cover
    def __init__(self, val):
        self.val = val

    def satisfied(self, what=None, inquiry=None):
        return True


@pytest.mark.integration
class TestMigration1x1x0To1x1x1:
    class MockLoggingHandler(logging.Handler):
        def __init__(self, *args, **kwargs):
            self.messages = {}
            super().__init__(*args, **kwargs)

        def emit(self, record):
            level = record.levelname.lower()
            if level not in self.messages:
                self.messages[level] = []
            self.messages[level].append(record.getMessage())

    @pytest.fixture()
    def storage(self):
        client = create_client()
        storage = MongoStorage(client, DB_NAME, collection=COLLECTION)
        yield storage
        client[DB_NAME][COLLECTION].remove()
        client.close()

    def test_order(self, storage):
        migration = Migration1x1x0To1x1x1(storage)
        assert 2 == migration.order

    def test_up(self, storage):
        migration = Migration1x1x0To1x1x1(storage)
        # prepare docs that might have been saved by users in v 1.1.0
        docs = [
            (
                """
                { "_id" : 10, "uid" : 10, "description" : null, "subjects" : [ ], "effect" : "allow", 
                "resources" : [ ], "actions" : [ ], "rules" : { "secret" : 
                "{\\"type\\": \\"vakt.rules.string.StringEqualRule\\", \\"contents\\": {\\"val\\": \\"i-am-a-foo\\"}}", 
                "name":"{\\"type\\": \\"vakt.rules.string.StringEqualRule\\", \\"contents\\":{\\"val\\": \\"Max\\"}}" }}
                """,
                """
                { "_id" : 10, "actions" : [ ], "description" : null, "effect" : "allow", "resources" : [ ], 
                "rules" : { "name" : {"py/object": "vakt.rules.string.StringEqualRule", "val": "Max" },
                "secret" : {"py/object": "vakt.rules.string.StringEqualRule", "val": "i-am-a-foo"} }, 
                "subjects" : [ ], "uid" : 10 }
                """
            ),
            (
                """
                { "_id" : 20, "uid" : 20, "description" : "foo bar", "subjects" : [ "<.*>" ], "effect" : "allow",
                "resources" : [ "<.*>" ], "actions" : [ "<.*>" ], "rules" : { "secret" :
                "{\\"type\\": \\"vakt.rules.string.StringEqualRule\\", \\"contents\\": {\\"val\\": \\"John\\"}}" } }
                """,
                """
                { "_id" : 20, "actions" : [ "<.*>" ], "description" : "foo bar", "effect" : "allow",
                "resources" : [ "<.*>" ], "rules" : { "secret" :
                { "py/object": "vakt.rules.string.StringEqualRule", "val": "John"} }, "subjects" : [ "<.*>" ],
                "uid" : 20 }
                """
            ),
            (
                """
                { "_id" : 30, "uid" : 30, "description" : "foo bar", "subjects" : [ "<.*>" ], "effect" : "allow",
                "resources" : [ "<.*>" ], "actions" : [ "<.*>" ], "rules" : {  } }
                """,
                """
                { "_id" : 30, "actions" : [ "<.*>" ], "description" : "foo bar", "effect" : "allow",
                "resources" : [ "<.*>" ], "rules" : {  }, "subjects" : [ "<.*>" ], "uid" : 30 }
                """
            ),
            (
                """
                { "_id" : 40, "uid" : 40, "description" : null, "subjects" : [ "<.*>" ], "effect" : "allow", 
                "resources" : [ "<.*>" ], "actions" : [ "<.*>" ], "rules" : 
                { "num" : "{\\"type\\": \\"test_storage_mongo.Simple\\", \\"contents\\": {\\"val\\": \\"123\\"}}", 
                "a" : "{\\"type\\": \\"vakt.rules.string.StringEqualRule\\", \\"contents\\": {\\"val\\": \\"foo\\"}}" }}
                """,
                """
                { "_id" : 40, "actions" : [ "<.*>" ], "description" : null, "effect" : "allow",  "resources" : ["<.*>"],
                "rules" : { "a" : {"py/object": "vakt.rules.string.StringEqualRule", "val": "foo"},
                "num" : { "py/object": "test_storage_mongo.Simple", "val": "123"} }, "subjects" : ["<.*>"], "uid" : 40 }
                """
            ),
            (
                """
                { "_id" : 50, "uid" : 50, "description" : null, "subjects" : [ ], "effect" : "allow", "resources" : [ ], 
                "actions" : [ ], "rules" : { "num" : 
                "{\\"type\\": \\"test_storage_mongo.Simple\\", \\"contents\\": {\\"val\\": \\"46\\"}}" } }
                """,
                """
                { "_id" : 50, "actions" : [ ], "description" : null, "effect" : "allow", "resources" : [ ],
                "rules" : { "num" : { "py/object": "test_storage_mongo.Simple", "val": "46"} },
                "subjects" : [ ], "uid" : 50 }
                """
            ),
        ]
        for (doc, _) in docs:
            d = b_json.loads(doc)
            migration.storage.collection.insert_one(d)

        migration.up()

        # test no new docs were added and no docs deleted
        assert len(docs) == migration.storage.collection.count()
        # test Policy.from_json() is called without errors for each doc (implicitly)
        assert len(docs) == len(list(migration.storage.get_all(1000, 0)))
        # test string contents of each doc and full guard allowance run
        g = Guard(migration.storage, RegexChecker())
        inq = Inquiry(action='foo', resource='bar', subject='Max', context={'val': 'foo', 'num': '123'})
        for (doc, result_doc) in docs:
            new_doc = migration.storage.collection.find_one({'uid': json.loads(doc)['uid']})
            expected = result_doc.replace("\n", '').replace(' ', '')
            actual = json.dumps(new_doc, sort_keys=True).replace("\n", '').replace(' ', '')
            assert expected == actual
            assert g.is_allowed(inq)

    def test_down(self, storage):
        assertions = unittest.TestCase('__init__')
        migration = Migration1x1x0To1x1x1(storage)
        # prepare docs that might have been saved by users in v 1.1.1
        docs = [
            (
                """
                {"_id":1,"actions":[],"description":null,"effect":"deny","resources":[],"rules":
                {"name":{"py/object":"vakt.rules.string.RegexMatchRule",
                "regex":{"pattern":"[Mm]ax","py/object":"_sre.SRE_Pattern"}},
                "secret":{"py/object":"vakt.rules.string.StringEqualRule","val":"i-am-a-foo"}},
                "subjects":[],"uid":1}
                """,
                None
            ),
            (
                """
                {"_id":2,"actions":["<.*>"],"description":"foobar","effect":"deny",
                "resources":["<.*>"],"rules":{"secret":{"py/object":"vakt.rules.string.StringEqualRule","val":"John"}},
                "subjects":["<.*>"],"uid":2}
                """,
                """
                {"_id":2,"actions":["<.*>"],"description":"foobar","effect":"deny",
                "resources":["<.*>"],"rules":{"secret":
                "{\\"contents\\": {\\"val\\": \\"John\\"}, \\"type\\": \\"vakt.rules.string.StringEqualRule\\"}"},
                "subjects":["<.*>"],"uid":2}
                """
            ),
            (
                """
                {"_id":3,"actions":["<.*>"],"description":"foobar","effect":"deny",
                "resources":["<.*>"],"rules":{},"subjects":["<.*>"],"uid":3}
                """,
                """
                {"_id":3,"actions":["<.*>"],"description":"foobar","effect":"deny",
                "resources":["<.*>"],"rules":{},"subjects":["<.*>"],"uid":3}
                """
            ),
            (
                """
                {"_id":4,"actions":[],"description":null,"effect":"deny","resources":[],
                "rules":{"digit":{"py/object":"test_storage_mongo.WithObject",
                "val":{"pattern":"\\\\d+","py/object":"_sre.SRE_Pattern"}},
                "num":{"py/object":"test_storage_mongo.Simple","val":"123"}},"subjects":[],"uid":4}
                """,
                None
            ),
            (
                """
                {"_id":5,"actions":[],"description":null,"effect":"deny","resources":[],"rules":
                {"num":{"py/object":"test_storage_mongo.Simple","val":"46"}},"subjects":[],"uid":5}
                """,
                """
                {"_id":5,"actions":[],"description":null,"effect":"deny","resources":[],"rules":
                {"num":"{\\"contents\\": {\\"val\\": \\"46\\"}, \\"type\\": \\"test_storage_mongo.Simple\\"}"},
                "subjects":[],"uid":5}
                """
            ),
            (
                """
                {"_id":"6","uid":"6"}
                """,
                None
            ),
        ]
        for (doc, _) in docs:
            d = b_json.loads(doc)
            migration.storage.collection.insert_one(d)

        # set logger for capturing output
        l = logging.getLogger('vakt.storage.mongo')
        log_handler = self.MockLoggingHandler()
        l.setLevel(logging.INFO)
        l.addHandler(log_handler)

        migration.down()

        # test no new docs were added and no docs deleted
        assert len(docs) == migration.storage.collection.count()
        # test Policy.from_json() is called without errors for each doc (implicitly)
        assert len(docs) == len(list(migration.storage.get_all(1000, 0)))
        # test string contents of each doc
        for (doc, expected_doc) in docs:
            if not expected_doc:  # some policies should be left as-is if not converted
                expected_doc = doc
            new_doc = migration.storage.collection.find_one({'uid': json.loads(doc)['uid']})
            assertions.assertDictEqual(json.loads(expected_doc), new_doc)
        # test failed policies report
        # info
        assert 'info' in log_handler.messages
        assert 9 == len(log_handler.messages['info'])
        assert 'Trying to migrate Policy with UID: 5' in log_handler.messages['info']
        assert 'Policy with UID was migrated: 5' in log_handler.messages['info']
        # warn
        assert 'warning' in log_handler.messages
        assert 2 == len(log_handler.messages['warning'])
        assert "Irreversible Policy. vakt.rules.string.RegexMatchRule could not be stored in v1.1.0. Mongo doc:" in \
               log_handler.messages['warning'][0]
        assert "'_id': 1" in log_handler.messages['warning'][0]
        assert "Irreversible Policy. Custom rule class contains non-primitive data {'" in \
               log_handler.messages['warning'][1]
        assert "'_id': 4" in log_handler.messages['warning'][1]
        # error
        assert 'error' in log_handler.messages
        assert 2 == len(log_handler.messages['warning'])
        assert "Unexpected exception occurred while migrating Policy:" in log_handler.messages['error'][0]
        assert "'uid': '6'" in log_handler.messages['error'][0]
        assert 'Migration was unable to convert some Policies, but' in log_handler.messages['error'][1]
        assert 'Mongo IDs of failed Policies are:' in log_handler.messages['error'][1]
        assert "[1, 4, '6']" in log_handler.messages['error'][1]
