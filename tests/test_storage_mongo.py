import pytest

from pymongo import MongoClient

from vakt.storage.mongo import MongoStorage
from vakt.policy import Policy
from vakt.guard import Inquiry
from vakt.exceptions import PolicyExistsError


@pytest.fixture
def st():
    client = MongoClient('localhost', 27017)
    return MongoStorage(client)


def test_add(st):
    st.add(Policy('1', description='foo'))
    assert '1' == st.get('1').uid
    assert 'foo' == st.get('1').description


def test_policy_create_existing(st):
    st.add(Policy('1', description='foo'))
    with pytest.raises(PolicyExistsError):
        st.add(Policy('1', description='bar'))


def test_get(st):
    pass


def test_get_all(st):
    pass


def test_get_all_for_one(st):
    pass


def test_find_for_inquiry(st):
    pass


def test_update(st):
    pass


def test_delete(st):
    pass
