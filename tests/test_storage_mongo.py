from urllib.parse import quote_plus
import uuid

import pytest
from pymongo import MongoClient
from bson.objectid import ObjectId

from vakt.storage.mongo import MongoStorage
from vakt.policy import Policy
from vakt.rules.string import StringEqualRule
from vakt.exceptions import PolicyExistsError


@pytest.fixture()
def st():
    db_name = 'my_app'
    collection_name = 'vakt'
    user, password = 'root', 'example'
    uri = 'mongodb://%s:%s@%s' % (quote_plus(user), quote_plus(password), 'localhost:27017')
    client = MongoClient(uri, socketTimeoutMS=5*1000)
    yield MongoStorage(client, db_name, collection=collection_name)
    client[db_name][collection_name].remove()
    client.close()


def test_add(st):
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


def test_add_with_bson_object_id(st):
    id = str(ObjectId())
    p = Policy(
        uid=id,
        description='foo',
    )
    st.add(p)

    back = st.get(id)
    assert id == back.uid


def test_policy_create_existing(st):
    id = str(uuid.uuid4())
    st.add(Policy(id, description='foo'))
    with pytest.raises(PolicyExistsError):
        st.add(st.add(Policy(id, description='bar')))


# def test_get(st):
#     pass
#
#
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
#
#
# def test_update(st):
#     pass
#
#
# def test_delete(st):
#     pass
