from unittest.mock import patch, mock_open

from vakt.readers.yaml import YamlReader
from vakt.effects import ALLOW_ACCESS


def test_read_onestring_based_definition():
    yaml = r"""
uid: asdf-qwerty
actions:
  - "<read|get>"
resources:
  - "library:books:<.+>"
  - "office:magazines:<.+>"
subjects:
  - "<[\w]+ M[\w]+>"
effect: allow
description: >
    Allow all readers of the book library whose surnames start with M get and read any book or magazine,
    but only when they connect from local library's computer
    """
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = reader.read()
        data = list(data)
        assert 1 == len(data)
        policy = data[0]
        assert 'asdf-qwerty' == policy.uid
        assert \
            'Allow to fork or clone any Google repository for users with > 50 and < 999 stars and came from Github'\
            == policy.description
        assert ALLOW_ACCESS == policy.effect
        assert [] == policy.subjects
        assert [] == policy.actions
        assert [] == policy.resources
        assert {} == policy.context


def test_read_several_definitions():
    yaml = """
uid: 1
actions:
  - Eq: fork
  - Eq: clone
resources:
  - StartsWith:
    - repos/Google
    - ci: True
subjects:
  - name: Any
    stars:
      - And:
        - Greater: 50
        - Less: 999
context:
  - referer:
    - Eq: https://github.com
effect: allow
description: >
  Allow to fork or clone any Google repository for users that
  have > 50 and < 999 stars and came from Github
    
---
    
uid: auto
actions:
  - Eq: fork
  - Eq: clone
resources:
  - StartsWith:
    - repos/Google
    - ci: True
subjects:
  - name: Any
    stars:
      - And:
        - Greater: 50
        - Less: 999
context:
  - referer:
    - Eq: https://github.com
effect: deny
description: >
  Allow to fork or clone any Google repository for users that
  have > 50 and < 999 stars and came from Github
    """
    with patch('vakt.readers.yaml.open', mock_open(read_data=yaml)):
        reader = YamlReader('foo/bar.yaml')
        data = reader.read()
        data = list(data)
        assert 2 == len(data)
