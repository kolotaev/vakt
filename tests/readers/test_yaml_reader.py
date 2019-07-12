from unittest.mock import patch, mock_open

import pytest

from vakt.readers.yaml import YamlReader
from vakt.effects import ALLOW_ACCESS, DENY_ACCESS
from vakt.exceptions import PolicyCreationError
import vakt.rules as r


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


@pytest.mark.parametrize('yaml, expect', [
    (
        """
        effect: allow
        """,
        [],
    ),
    (
        """
        effect: allow
        actions: []
        """,
        [],
    ),
    (
        """
        effect: allow
        actions:
          - Any:
        """,
        [r.Any()],
    ),
    (
        """
        effect: allow
        actions:
          - Any:
          - Any:
        """,
        [r.Any(), r.Any()],
    ),
    (
        """
        effect: allow
        actions:
          - Any:
          - Neither:
          - Truthy:
        """,
        [r.Any(), r.Neither(), r.Truthy()],
    ),
    (
        """
        effect: allow
        actions:
          - Eq: 123
        """,
        [r.Eq(123)],
    ),
    (
        """
        effect: allow
        actions:
          - Eq: 123
          - Eq: 456
        """,
        [r.Eq(123), r.Eq(456)],
    ),
    (
        """
        effect: allow
        actions:
          - In:
            - 12
            - 99
            - 88
        """,
        [r.In(12, 99, 88)],
    ),
    (
        """
        effect: allow
        actions:
          - In: [22, 44, 77]
        """,
        [r.In(22, 44, 77)],
    ),
    (
        """
        effect: allow
        actions:
          - In: []
        """,
        [r.In()],
    ),
    (
        """
        effect: allow
        actions:
          - In:
        """,
        [r.In()],
    ),
    (
        """
        effect: allow
        actions:
          - StartsWith:
            - "foo-"
            - ci: true
        """,
        [r.StartsWith('foo-', ci=True)],
    ),
    (
        """
        effect: allow
        actions:
          - StartsWith:
            - "foo-"
        """,
        [r.StartsWith('foo-', ci=False)],
    ),
])
def test_rule_attributes_definition_variants(yaml, expect):
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = list(reader.read())
        expected_actions = [a.to_json(sort=True) for a in expect]
        actual_actions = [a.to_json(sort=True) for a in data[0].actions]
        assert expected_actions == actual_actions


@pytest.mark.parametrize('yaml', [
    (
        """
        effect: allow
        actions:
          - StartsWith:
        """,
    ),
])
def test_rule_attributes_definition_bad_variants(yaml):
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        with pytest.raises(PolicyCreationError) as excinfo:
            d = reader.read()
            _ = list(d)
        assert 'Unknown policy effect: ""' in str(excinfo.value)
