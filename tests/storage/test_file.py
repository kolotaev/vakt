from unittest.mock import patch, mock_open

import pytest

from vakt.storage.file import FileStorage
from vakt.policy import Policy


@pytest.fixture
def st():
    with patch('vakt.readers.abc.open', mock_open(read_data='')):
        with patch('vakt.readers.json.open', mock_open(read_data='{}')):
            yield FileStorage('foo/bar.json')


def test_init_file_does_not_exist():
    with pytest.raises(RuntimeError) as excinfo:
        FileStorage('foo/bar.json')
    assert 'Failed to created reader from file foo/bar.json. Errors: ' + \
           '["Try to read with JSONReader - got [Errno 2] No such file or directory: \'foo/bar.json\'", ' + \
           '"Try to read with YamlReader - got [Errno 2] No such file or directory: \'foo/bar.json\'"]' \
           == str(excinfo.value)


def test_init_json_file_is_malformed():
    with pytest.raises(Exception) as excinfo:
        with patch('vakt.readers.abc.open', mock_open(read_data='aaaa_bbb')):
            with patch('vakt.readers.json.open', mock_open(read_data='aaaa_bbb')):
                FileStorage('foo/bar.json')
    assert 'Reader JSONReader failed to read Policy. Caused by: ' + \
           'Expecting value: line 1 column 1 (char 0). Data was: aaaa_bbb' \
           == str(excinfo.value)


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
