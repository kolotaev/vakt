import uuid
import random
import types
import logging
import io
from unittest.mock import Mock

import pytest
from redis import Redis

from vakt.storage.redis import RedisStorage, JSONSerializer, PickleSerializer
from vakt.policy import Policy
from vakt.rules.string import Equal
from vakt.rules.logic import Any, And
from vakt.rules.operator import Eq, Greater
from vakt.exceptions import PolicyExistsError
from vakt.guard import Inquiry
from vakt.checker import StringExactChecker, StringFuzzyChecker, RegexChecker, RulesChecker


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
DB = 0
COLLECTION = 'vakt_policies_test'


def create_client():
    return Redis(REDIS_HOST, REDIS_PORT, DB)


@pytest.mark.integration
class TestRedisStorage:

    # We test storage with all available serializers
    @pytest.fixture(params=[JSONSerializer(), PickleSerializer()])
    def st(self, request):
        client = create_client()
        yield RedisStorage(client, collection=COLLECTION, serializer=request.param)
        client.flushdb()
        client.close()

    @pytest.fixture()
    def log(self):
        al = logging.getLogger('vakt.storage.redis')
        initial_handlers = al.handlers[:]
        initial_level = al.getEffectiveLevel()
        yield al
        al.handlers = initial_handlers
        al.setLevel(initial_level)

    def test_storage_uses_pickle_serializer_by_default(self):
        client = create_client()
        try:
            s = RedisStorage(client, collection=COLLECTION)
            sr = s.sr
            assert isinstance(sr, PickleSerializer)
        finally:
            client.close()

    def test_add(self, st):
        id = str(uuid.uuid4())
        p = Policy(
            uid=id,
            description='foo bar баз',
            subjects=('Edward Rooney', 'Florence Sparrow'),
            actions=['好'],
            resources=['<.*>'],
            context={
                'secret': Equal('i-am-a-teacher'),
                'rating': And(Eq(80), Greater(80))
            },
        )
        st.add(p)
        back = st.get(id)
        assert id == back.uid
        assert 'foo bar баз' == back.description
        assert isinstance(back.context['secret'], Equal)
        assert isinstance(back.context['rating'], And)
        assert '好' == back.actions[0]
        st.add(Policy('2', actions=[Eq('get'), Eq('put')], subjects=[Any()], resources=[{'books': Eq('Harry')}]))
        assert '2' == st.get('2').uid
        assert 2 == len(st.get('2').actions)
        assert 1 == len(st.get('2').subjects)
        assert isinstance(st.get('2').subjects[0], Any)
        assert 1 == len(st.get('2').resources)
        assert isinstance(st.get('2').resources[0]['books'], Eq)
        assert 'Harry' == st.get('2').resources[0]['books'].val

    def test_policy_create_existing(self, st):
        uid = str(uuid.uuid4())
        st.add(Policy(uid, description='foo'))
        with pytest.raises(PolicyExistsError):
            st.add(Policy(uid, description='bar'))

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
        (10000, 0, 20),
        (5, 18, 2),
        (5, 19, 1),
        (5, 20, 0),
        (5, 21, 0),
    ])
    def test_get_all(self, st, limit, offset, result):
        for i in range(20):
            desc = ''.join(random.choice('abcde') for _ in range(30))
            st.add(Policy(str(i), description=desc))
        policies = list(st.get_all(limit=limit, offset=offset))
        ll = len(policies)
        assert result == ll

    def test_get_all_for_empty_database(self, st):
        assert [] == list(st.get_all(limit=100, offset=0))

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
        assert ['Edward Rooney', 'Florence Sparrow'] == policies[0].subjects or \
               ('Edward Rooney', 'Florence Sparrow') == policies[0].subjects
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
        pols = []
        for p in found:
            pols.append(p.uid)
        assert 2 == len(pols)

    @pytest.mark.parametrize('checker, expect_number', [
        (None, 6),
        (RegexChecker(), 6),
        (RulesChecker(), 6),
        (StringExactChecker(), 6),
        (StringFuzzyChecker(), 6),
    ])
    def test_find_for_inquiry_returns_all_policies_for_any_checker_and_inquiry(self, st, checker, expect_number):
        st.add(Policy('1', subjects=['<[mM]ax>', '<.*>']))
        st.add(Policy('2', subjects=['sam<.*>', 'foo']))
        st.add(Policy('3', subjects=['Jim'], actions=['delete'], resources=['server']))
        st.add(Policy('3.1', subjects=['Jim'], actions=[r'del<\w+>'], resources=['server']))
        st.add(Policy('4', subjects=[{'stars': Eq(90)}, Eq('Max')]))
        st.add(Policy('5', subjects=[Eq('Jim'), Eq('Nina')]))
        inquiry = Inquiry(subject='Jim', action='delete', resource='server')
        found = st.find_for_inquiry(inquiry, checker)
        assert expect_number == len(list(found))

    def test_find_for_inquiry_for_empty_database(self, st):
        assert [] == list(st.find_for_inquiry(Inquiry(), RegexChecker()))

    def test_find_for_inquiry_returns_generator(self, st):
        st.add(Policy('1', subjects=['max', 'bob'], actions=['get'], resources=['comics']))
        st.add(Policy('2', subjects=['max', 'bob'], actions=['get'], resources=['comics']))
        inquiry = Inquiry(subject='max', action='get', resource='comics')
        found = st.find_for_inquiry(inquiry)
        assert isinstance(found, types.GeneratorType)
        pols = []
        for p in found:
            pols.append(p.uid)
        assert 2 == len(pols)

    def test_find_for_inquiry_returns_empty_list_if_nothing_is_returned(self, st):
        inquiry = Inquiry(subject='max', action='get', resource='comics')
        assert [] == st.find_for_inquiry(inquiry)
        mock_client = Mock(spec=Redis, **{'hgetall.side_effect': [None]})
        st.client = mock_client
        assert [] == st.find_for_inquiry(inquiry)

    def test_update(self, st):
        id = str(uuid.uuid4())
        policy = Policy(id)
        st.add(policy)
        assert id == st.get(id).uid
        assert None is st.get(id).description
        assert () == st.get(id).actions or [] == st.get(id).actions
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

    def test_update_non_existing_does_not_create_anything(self, st, log):
        log_capture_str = io.StringIO()
        h = logging.StreamHandler(log_capture_str)
        h.setLevel(logging.INFO)
        log.setLevel(logging.INFO)
        log.addHandler(h)
        # test
        uid = str(uuid.uuid4())
        st.update(Policy(uid, actions=['get'], description='bar'))
        assert '' == log_capture_str.getvalue().strip()
        assert st.get(uid) is None

    def test_delete(self, st, log):
        policy = Policy('1')
        st.add(policy)
        assert '1' == st.get('1').uid
        log_capture_str = io.StringIO()
        h = logging.StreamHandler(log_capture_str)
        h.setLevel(logging.INFO)
        log.setLevel(logging.INFO)
        log.addHandler(h)
        # test
        st.delete('1')
        assert 'Deleted Policy with UID=1' == log_capture_str.getvalue().strip()
        assert None is st.get('1')

    def test_delete_nonexistent(self, st, log):
        log_capture_str = io.StringIO()
        h = logging.StreamHandler(log_capture_str)
        h.setLevel(logging.INFO)
        log.setLevel(logging.INFO)
        log.addHandler(h)
        # test
        uid = '123456789_not_here'
        st.delete(uid)
        assert 'Nothing to delete by UID=123456789_not_here' == log_capture_str.getvalue().strip()
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

    def test_custom_pickle_serializer_works(self, st):
        st.sr = PickleSerializer(3, fix_imports=False)
        st.add(Policy('1'))
        st.add(Policy(2, description='some text'))
        assert isinstance(st.get('1'), Policy)
        assert '1' == st.get('1').uid
        assert 2 == st.get(2).uid
        assert 'some text' == st.get(2).description
