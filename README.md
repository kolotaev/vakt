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

Vakt runs on Python >= 3.3.
PyPy implementation is supported as well.

```bash
pip install vakt
```

### Concepts

### Managers

#### Memory

### Usage

### Components

#### Policies

### JSON

All Policies, Inquiries and Rules can be JSON-serialized and deserialized.

For example, for a Policy all you need is just run:
```python
from vakt.policy import DefaultPolicy

policy = DefaultPolicy('1')

json_policy = policy.to_json()
print(json_policy)
# {"actions": [], "description": null, "effect": "deny", "id": "1", "resources": [], "rules": {}, "subjects": []}

policy = DefaultPolicy.from_json(json_policy)
print(policy)
# <vakt.policy.DefaultPolicy object at 0x1023ca198>
```

The same goes for Rules, Inquiries.
All custom classes derived from them support this functionality as well.
If you do not derive from Vakt's classes, but want this option, you can mix-in `vakt.util.JsonDumper` trait.

```python
from vakt.util import JsonDumper

class CustomInquiry(JsonDumper):
    pass
```

### Logging

Vakt follows a common logging pattern for libraries:
Its corresponding modules log all the events that happen but the log messages by default are handled by `NullHandler`.
It's up to the outer code/application to provide a valid log-handler and a desired level of logging. For example:

```python
import logging

root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(logging.StreamHandler())

... # here go all the Vakt calls.
```

Vakt logs can be separated in 2 basic areas:
1. Error/Exception level - inform about exceptions and errors during Vakt work.
2. Info level - inform about incoming inquires and their resolution.


### Development

To hack Vakt locally run:

```bash
pip install -e .[dev] -r requirements.txt            # to install all dependencies
pytest                                               # to run tests with coverage report
pytest --cov-config .coveragerc --cov=vakt tests/    # to get coverage report
pylint vakt                                          # to check code quality with PyLint
```
