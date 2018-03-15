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
- [Storage](#storage)
    - [Memory](#memory)
- [Usage](#usage)
- [Components](#components)
	- [Policy](#policy)
	- [Inquiry](#inquiry)
	- [Rule](#rule)
	- [Checker](#checker)
	- [Guard](#guard)
- [JSON](#json)
- [Logging](#logging)
- [Benchmark](#benchmark)
- [Development](#development)


### Description

### Install

Vakt runs on Python >= 3.3.
PyPy implementation is supported as well.

```bash
pip install vakt
```

### Concepts

### Storage

#### Memory

### Usage

### Components

#### Policy
#### Inquiry
#### Rule
#### Checker
#### Guard

### JSON

All Policies, Inquiries and Rules can be JSON-serialized and deserialized.

For example, for a Policy all you need is just run:
```python
from vakt.policy import Policy

policy = Policy('1')

json_policy = policy.to_json()
print(json_policy)
# {"actions": [], "description": null, "effect": "deny", "id": "1",
# "resources": [], "rules": {}, "subjects": []}

policy = Policy.from_json(json_policy)
print(policy)
# <vakt.policy.Policy object at 0x1023ca198>
```

The same goes for Rules, Inquiries.
All custom classes derived from them support this functionality as well.
If you do not derive from Vakt's classes, but want this option, you can mix-in `vakt.util.JsonDumper` class.

```python
from vakt.util import JsonDumper

class CustomInquiry(JsonDumper):
    pass
```

### Logging

Vakt follows a common logging pattern for libraries:

Its corresponding modules log all the events that happen but the log messages by default are handled by `NullHandler`.
It's up to the outer code/application to provide desired log handlers, filters, levels, etc. For example:

```python
import logging

root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(logging.StreamHandler())

... # here go all the Vakt calls.
```

Vakt logs can be considered in 2 basic levels:
1. Error/Exception - informs about exceptions and errors during Vakt work.
2. Info - informs about incoming inquires and their resolution.


### Benchmark

You can see how much time it takes a single Inquiry to be processed given we have a number of unique Policies in Memory
Store.

Example:

```bash
python3 benchmark.py 1000 no

Output is:
# Number of unique Policies in DB: 1,000
# Are Policies defined in Regex syntax?: False
# Single Inquiry decision took: 0.0041 seconds
# Inquiry allowed? False
```

Script arguments:
1. Int - Number of unique Policies generated and put into Storage (Default: 100,000)
2. 'no/yes' - Should Policies be generated using regex syntax rules or not? (Default: yes)


### Development

To hack Vakt locally run:

```bash
pip install -e .[dev] -r requirements.txt            # to install all dependencies
pytest                                               # to run tests with coverage report
pytest --cov-config .coveragerc --cov=vakt tests/    # to get coverage report
pylint vakt                                          # to check code quality with PyLint
```
