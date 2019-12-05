import pytest

from vakt.storage.memory import MemoryStorage
from vakt.storage.observable import ObservableMutationStorage
from ..helper import CountObserver
from vakt import Policy, Inquiry


class TestObservableMutationStorage:

    @pytest.fixture()
    def factory(self):
        def objects_factory():
            mem = MemoryStorage()
            st = ObservableMutationStorage(mem)
            observer = CountObserver()
            st.add_listener(observer)
            return st, mem, observer
        return objects_factory

    def test_add(self, factory):
        st, mem, observer = factory()
        p1 = Policy(1)
        p2 = Policy(2)
        p3 = Policy(3)
        st.add(p1)
        st.add(p2)
        assert 2 == observer.count
        assert 2 == len(list(mem.retrieve_all()))
        assert 2 == len(list(st.retrieve_all()))
        st.add(p3)
        assert 3 == observer.count

    def test_get(self, factory):
        st, mem, observer = factory()
        p1 = Policy('a')
        st.add(p1)
        assert 'a' == st.get('a').uid
        assert 'a' == mem.get('a').uid
        assert 1 == observer.count
        assert None is st.get('b')
        assert None is mem.get('b')
        assert 1 == observer.count

    def test_update(self, factory):
        st, mem, observer = factory()
        p1 = Policy('a')
        st.add(p1)
        p1.uid = 'b'
        st.update(p1)
        assert 'b' == list(mem.retrieve_all())[0].uid
        assert 'b' == list(st.retrieve_all())[0].uid
        assert 2 == observer.count
        p1.uid = 'c'
        st.update(p1)
        assert 3 == observer.count

    def test_delete(self, factory):
        st, mem, observer = factory()
        p1 = Policy('a')
        st.add(p1)
        st.delete('a')
        assert [] == list(mem.retrieve_all())
        assert [] == list(st.retrieve_all())
        assert 2 == observer.count
        st.delete('a')
        assert [] == list(mem.retrieve_all())
        assert [] == list(st.retrieve_all())
        assert 3 == observer.count

    def test_retrieve_all(self, factory):
        st, mem, observer = factory()
        p1 = Policy('a')
        st.add(p1)
        assert 'a' == list(mem.retrieve_all())[0].uid
        assert 'a' == list(st.retrieve_all())[0].uid
        assert 1 == observer.count
        assert 'a' == list(mem.retrieve_all(batch=2))[0].uid
        assert 'a' == list(st.retrieve_all(batch=2))[0].uid
        assert 1 == observer.count
        assert 'a' == list(mem.retrieve_all(5))[0].uid
        assert 'a' == list(st.retrieve_all(5))[0].uid
        assert 1 == observer.count

    def test_get_all(self, factory):
        st, mem, observer = factory()
        p1 = Policy('a')
        st.add(p1)
        assert 'a' == list(mem.get_all(5, 0))[0].uid
        assert 'a' == list(st.get_all(5, 0))[0].uid
        assert 1 == observer.count
        st.get_all(9, 0)
        st.get_all(888, 0)
        assert 1 == observer.count

    def test_find_for_inquiry(self, factory):
        st, mem, observer = factory()
        inq = Inquiry(action='get', subject='foo', resource='bar')
        p1 = Policy('a')
        p2 = Policy('b')
        st.add(p1)
        st.add(p2)
        mem_found = list(mem.find_for_inquiry(inq))
        assert [p1, p2] == mem_found or [p2, p1] == mem_found
        st_found = list(st.find_for_inquiry(inq))
        assert [p1, p2] == st_found or [p2, p1] == st_found
        assert 2 == observer.count
        st.find_for_inquiry(inq)
        st.find_for_inquiry(inq)
        assert 2 == observer.count
