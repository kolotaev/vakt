from vakt.util import JsonSerializer, Subject, Observer


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
    class MyObserver(Observer):
        def __init__(self):
            self.counter = 0

        def update(self):
            self.counter += 1

    subj = Subject()
    o1 = MyObserver()
    o2 = MyObserver()
    subj.add_listener(o1)
    subj.add_listener(o2)
    subj.notify()
    subj.notify()
    assert 2 == o1.counter
    assert 2 == o2.counter
    subj.remove_listener(o1)
    subj.notify()
    assert 2 == o1.counter
    assert 3 == o2.counter
