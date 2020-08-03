from unittest.mock import patch, mock_open

import pytest

from vakt.storage.file import FileStorage
from vakt.policy import Policy


@pytest.fixture
def st():
    with patch('vakt.readers.json.open', mock_open(read_data='{}')):
        yield FileStorage('foo/bar.json')


def test_add(st):
    with pytest.raises(NotImplementedError) as excinfo:
        p = Policy(1)
        st.add(p)
    assert 'Please, add Policy in file manually' in str(excinfo.value)


def test_update(st):
    with pytest.raises(NotImplementedError) as excinfo:
        p = Policy(1)
        st.update(p)
    assert 'Please, update Policy in file manually' in str(excinfo.value)


def test_delete(st):
    with pytest.raises(NotImplementedError) as excinfo:
        p = Policy(1)
        st.delete(p)
    assert 'Please, delete Policy in file manually' in str(excinfo.value)
