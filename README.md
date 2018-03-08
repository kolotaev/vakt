# Vakt

[![Build Status](https://travis-ci.org/kolotaev/vakt.svg?branch=master)](https://travis-ci.org/kolotaev/vakt)
[![codecov.io](https://codecov.io/github/kolotaev/vakt/coverage.svg?branch=master)](https://codecov.io/github/kolotaev/vakt?branch=master)
[![Apache 2.0 licensed](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://raw.githubusercontent.com/kolotaev/vakt/master/LICENSE)

# WIP

Access policies SDK for Python.

## Documentation

- [Description](#description)
- [Install](#install)
- [Concepts](#concepts)
- [Managers](#managers)
    - [Memory](#memory)
- [Usage](#usage)
- [Components](#components)
	- [Policies](#policies)
	- [JSON](#json)
- [Logging](#logging)
- [Development](#development)


### Description

### Install

Vakt runs on Python >= 3.3. Also PyPy implementation is supported.

```bash
pip install vakt
```

### Concepts

### Managers

#### Memory

### Usage

### Components

#### Policies

#### JSON

All Policies, Requests and Rules can be JSON-serialized and deserialized.

For example, for a Policy all you need is just run:
```python
from vakt.policy import DefaultPolicy

policy = DefaultPolicy.from_json(json_encoded_policy)
policies = (DefaultPolicy('1'), DefaultPolicy('2'))
json_encoded_policies = DefaultPolicy.to_json(policies)

print(json_encoded_policies)
```

The same goes for Rules, Requests.
All custom classes derived from them support this functionality as well.
If you do not derive from Vakt's classes, but want this option, you can mix-in `vakt.util.JsonDumper` trait.

```python
from vakt.util import JsonDumper

class CustomRequest(JsonDumper):
    def __init__(self, resource=None, action=None, subject=None, context=None):
        pass
```

### Logging


### Development

