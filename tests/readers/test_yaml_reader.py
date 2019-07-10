from unittest.mock import patch, mock_open

import pytest

from vakt.readers.yaml import YamlReader
from vakt.effects import ALLOW_ACCESS, DENY_ACCESS
from vakt.exceptions import PolicyCreationError
from vakt.rules import Eq


def test_read_string_based_definition():
    yaml = r"""
uid: asdf-qwerty
actions:
  - "<read|get>"
resources:
  - 'library:books:<.+>'
  - 'office:magazines:<.+>'
subjects:
  - '<[\w]+ M[\w]+>'
effect: allow
description: Allow all readers of the book library whose surnames start with M
    """
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = reader.read()
        data = list(data)
        assert 1 == len(data)
        policy = data[0]
        assert 'asdf-qwerty' == policy.uid
        assert 'Allow all readers of the book library whose surnames start with M' == policy.description
        assert ALLOW_ACCESS == policy.effect
        assert [r'<[\w]+ M[\w]+>'] == policy.subjects
        assert ['<read|get>'] == policy.actions
        assert ['library:books:<.+>', 'office:magazines:<.+>'] == policy.resources
        assert {} == policy.context


def test_read_several_definitions():
    yaml = r"""
uid: 1
actions:
  - "<read|get>"
resources:
  - 'library:books:<.+>'
  - 'office:magazines:<.+>'
subjects:
  - '<[\w]+ M[\w]+>'
effect: allow
description: Allow all readers of the book library whose surnames start with M
    
---
    
uid: 2
actions:
  - "<read|post>"
resources:
  - 'office:magazines:<.+>'
subjects:
  - '<[\w]+ M[\w]+>'
effect: deny
    """
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = reader.read()
        data = list(data)
        assert 2 == len(data)


def test_bad_effect():
    yaml = r"""
uid: 1
actions:
  - "<read|get>"
resources:
  - bar
  - baz
subjects:
  - foo
effect: unknown
    """
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = reader.read()
        with pytest.raises(PolicyCreationError) as excinfo:
            list(data)
        assert 'Unknown policy effect: "unknown"' in str(excinfo.value)


def test_good_effect():
    yaml = r"""
uid: 1
actions:
  - "<read|get>"
resources:
  - bar
  - baz
subjects:
  - foo
effect: allow

---

uid: 1
actions:
  - "<read|get>"
resources:
  - bar
  - baz
subjects:
  - foo
effect: deny
    """
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = reader.read()
        policies = list(data)
        assert ALLOW_ACCESS == policies[0].effect
        assert DENY_ACCESS == policies[1].effect


def test_no_effect_specified():
    yaml = r"""
uid: 1
actions:
  - "<read|get>"
resources:
  - bar
  - baz
subjects:
  - foo
    """
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = reader.read()
        with pytest.raises(PolicyCreationError) as excinfo:
            list(data)
        assert 'Unknown policy effect: ""' in str(excinfo.value)


def test_auto_uids():
    yaml = r"""
uid: asdf
effect: allow

---

effect: deny

---

effect: deny

---

effect: allow

---

uid: qwer
effect: allow

---

effect: deny
    """
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = list(reader.read())
        assert ['asdf', 1, 2, 3, 'qwer', 4] == list(map(lambda x: x.uid, data))
        assert [ALLOW_ACCESS, DENY_ACCESS, DENY_ACCESS, ALLOW_ACCESS, ALLOW_ACCESS, DENY_ACCESS] == \
               list(map(lambda x: x.effect, data))


def test_stripping():
    yaml = r"""
uid: asdf     
effect:    allow   
description: >
    foo bar baz    
    baz     
    """
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = list(reader.read())
        assert 'foo bar baz     baz' == data[0].description
        assert ALLOW_ACCESS == data[0].effect
        assert 'asdf' == data[0].uid


@pytest.mark.parametrize('yaml, result', [
    (
        """
        effect: allow
        actions:
          - Eq: 123
        """,
        [Eq(123)],
    ),
])
def test_rule_definition_variants(yaml, result):
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = list(reader.read())
        assert result == data[0].actions
