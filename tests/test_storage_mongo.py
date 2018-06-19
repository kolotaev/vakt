from urllib.parse import quote_plus
import uuid

import pytest
from pymongo import MongoClient
from bson.objectid import ObjectId

from vakt.storage.mongo import MongoStorage
from vakt.policy import Policy
from vakt.rules.string import StringEqualRule
from vakt.exceptions import PolicyExistsError


@pytest.mark.integration
class TestMongoStorage(object):

    @pytest.fixture()
    def st(self):
        db_name, collection_name = 'my_app', 'vakt'
        user, password, host = 'root', 'example', 'localhost:27017'
        uri = 'mongodb://%s:%s@%s' % (quote_plus(user), quote_plus(password), host)
        client = MongoClient(uri, socketTimeoutMS=5*1000)
        yield MongoStorage(client, db_name, collection=collection_name)
        client[db_name][collection_name].remove()
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

    # def test_get_all(st):
    #     pass
    #
    #
    # def test_get_all_for_one(st):
    #     pass
    #
    #
    # def test_find_for_inquiry(st):
    #     pass

    def test_update(self, st):
        id = str(uuid.uuid4())
        policy = Policy(id)
        st.add(policy)
        assert id == st.get(id).uid
        assert None is st.get(id).description
        assert [] is st.get(id).actions
        policy.description = 'foo'
        policy.actions = ['a', 'b', 'c']
        st.update(policy)
        assert id == st.get(id).uid
        assert 'foo' == st.get(id).description
        assert ['a', 'b', 'c'] == st.get(id).actions

    def test_update_non_existing(self, st):
        id = str(uuid.uuid4())
        st.update(Policy(id, actions=['get'], description='bar'))
        assert id != st.get(id).uid
        assert 'bar' != st.get(id).description
        assert ['get'] != st.get(id).actions

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
