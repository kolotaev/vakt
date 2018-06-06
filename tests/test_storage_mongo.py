from urllib.parse import quote_plus
import uuid

import pytest
from pymongo import MongoClient

from vakt.storage.mongo import MongoStorage
from vakt.policy import Policy
from vakt.rules.string import StringEqualRule

from vakt.guard import Inquiry
from vakt.exceptions import PolicyExistsError


@pytest.fixture
def st():
    uri = 'mongodb://%s:%s@%s' % (quote_plus('root'), quote_plus('example'), 'localhost:27017')
    client = MongoClient(uri)
    return MongoStorage(client, 'my_app')


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

#
# def test_policy_create_existing(st):
#     pass
#
#
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
