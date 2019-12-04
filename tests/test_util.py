from vakt.util import JsonSerializer, Subject
from .helper import CountObserver


class AB(JsonSerializer):
    def __init__(self, b):
        self.b = b

    def _data(self):
        return self


class CD(JsonSerializer):
    def _data(self):
        return {'x': 1}


def test_json_serializer_from_json():
    js = AB(5).to_json()
    ab = AB.from_json(js)
    assert isinstance(ab, AB)
    js = CD().to_json()
    cd = CD.from_json(js)
    assert isinstance(cd, dict)
    assert cd == {'x': 1}


def test_observables():
    subj = Subject()
    o1 = CountObserver()
    o2 = CountObserver()
    subj.add_listener(o1)
    subj.add_listener(o2)
    subj.notify()
    subj.notify()
    assert 2 == o1.count
    assert 2 == o2.count
    subj.remove_listener(o1)
    subj.notify()
    assert 2 == o1.count
    assert 3 == o2.count
