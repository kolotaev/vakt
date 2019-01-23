from vakt.util import JsonSerializer


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
