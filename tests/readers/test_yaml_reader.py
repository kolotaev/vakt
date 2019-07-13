from unittest.mock import patch, mock_open

import pytest

from vakt.readers.yaml import YamlReader
from vakt.effects import ALLOW_ACCESS, DENY_ACCESS
from vakt.exceptions import PolicyCreationError
import vakt.rules as r
from vakt.policy import Policy


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
        effect: deny
        """,
        Policy(1),
    ),
    (
        """
        effect: deny
        actions: []
        """,
        Policy(1),
    ),
    (
        """
        effect: deny
        actions:
          - Any:
        """,
        Policy(1, actions=[r.Any()]),
    ),
    (
        """
        effect: deny
        actions:
          - Any:
          - Any:
        """,
        Policy(1, actions=[r.Any(), r.Any()]),
    ),
    (
        """
        effect: deny
        actions:
          - Any:
          - Neither:
          - Truthy:
        """,
        Policy(1, actions=[r.Any(), r.Neither(), r.Truthy()]),
    ),
    (
        """
        effect: deny
        actions:
          - Eq: 123
        """,
        Policy(1, actions=[r.Eq(123)]),
    ),
    (
        """
        effect: deny
        actions:
          - Eq: 123
          - Eq: 456
        """,
        Policy(1, actions=[r.Eq(123), r.Eq(456)]),
    ),
    (
        """
        effect: deny
        actions:
          - In:
            - 12
            - 99
            - 88
        """,
        Policy(1, actions=[r.In(12, 99, 88)]),
    ),
    (
        """
        effect: deny
        actions:
          - In: [22, 44, 77]
        """,
        Policy(1, actions=[r.In(22, 44, 77)]),
    ),
    (
        """
        effect: deny
        actions:
          - In:
            - 12
            - 99
            - 88
          - NotIn:
            - 77
            - 4
          - Greater: -9.89
        """,
        Policy(1, actions=[r.In(12, 99, 88), r.NotIn(77, 4), r.Greater(-9.89)]),
    ),
    (
        """
        effect: deny
        actions:
          - In: []
        """,
        Policy(1, actions=[r.In()]),
    ),
    (
        """
        effect: deny
        actions:
          - In:
        """,
        Policy(1, actions=[r.In()]),
    ),
    (
        """
        effect: deny
        actions:
          - StartsWith:
            - "foo-"
            - ci: true
        """,
        Policy(1, actions=[r.StartsWith('foo-', ci=True)]),
    ),
    (
        """
        effect: deny
        actions:
          - StartsWith:
            - "foo-"
        """,
        Policy(1, actions=[r.StartsWith('foo-', ci=False)]),
    ),
    (
        """
        effect: deny
        actions:
          - StartsWith:
            - "foo-"
          - EndsWith:
            - er
            - ci: yes
        """,
        Policy(1, actions=[r.StartsWith('foo-', ci=False), r.EndsWith('er', ci=True)]),
    ),
    (
        """
        effect: deny
        actions:
          - StartsWith:
            - "foo-"
          - Any:
          - EndsWith:
            - er
            - ci: yes
          - Eq: 890
        """,
        Policy(1, actions=[r.StartsWith('foo-', ci=False), r.Any(), r.EndsWith('er', ci=True), r.Eq(890)]),
    ),
    (
        """
        effect: deny
        actions:
        - nick:
          - Any:
        """,
        Policy(1, actions=[{'nick': r.Any()}]),
    ),
    (
        """
        effect: deny
        actions:
        - nick:
          - Eq: otter
        """,
        Policy(1, actions=[{'nick': r.Eq('otter')}]),
    ),
    (
        """
        effect: deny
        actions:
        - nick:
          - Eq: otter
          stars:
          - Greater: 90
        """,
        Policy(1, actions=[{'nick': r.Eq('otter'), 'stars': r.Greater(90)}]),
    ),
    (
        """
        effect: deny
        actions:
        - nick:
          - Eq: otter
          first_name:
          - EndsWith:
            - er
            - ci: yes
        """,
        Policy(1, actions=[{'nick': r.Eq('otter'), 'first_name': r.EndsWith('er', ci=True)}]),
    ),
    (
        """
        effect: deny
        actions:
        - nick:
          - Eq: otter
          first_name:
          - EndsWith:
            - er
            - ci: yes
        - role:
          - Eq: admin
        - sex:
          - In:
            - male
            - female
        """,
        Policy(1, actions=[
            {'nick': r.Eq('otter'), 'first_name': r.EndsWith('er', ci=True)},
            {'role': r.Eq('admin')},
            {'sex': r.In('male', 'female')}
        ]),
    ),
])
def test_rule_attributes_definition_variants(yaml, expect):
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = list(reader.read())
        expected_policy = expect.to_json(sort=True)
        actual_policy = data[0].to_json(sort=True)
        assert expected_policy == actual_policy


@pytest.mark.skip('fixme')
@pytest.mark.parametrize('yaml', [
    (
        """
        effect: allow
        actions:
          - StartsWith:
        """
    ),
])
def test_rule_attributes_definition_bad_variants(yaml):
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        # todo raise
        with pytest.raises(PolicyCreationError) as excinfo:
            d = reader.read()
            _ = list(d)
        assert 'Unknown policy effect: ""' in str(excinfo.value)
