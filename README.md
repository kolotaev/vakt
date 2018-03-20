# Vakt

[![Build Status](https://travis-ci.org/kolotaev/vakt.svg?branch=master)](https://travis-ci.org/kolotaev/vakt)
[![codecov.io](https://codecov.io/github/kolotaev/vakt/coverage.svg?branch=master)](https://codecov.io/github/kolotaev/vakt?branch=master)
[![Apache 2.0 licensed](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://raw.githubusercontent.com/kolotaev/vakt/master/LICENSE)

# WIP

Policy-based access control SDK for Python.

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

Vakt is an access control toolkit based on policies. It stands somewhere in-between RBAC and ACL models, giving you
a fine-grained control on definition of the rules that restrict an access to resources.
It highly resembles [IAM Policies](https://github.com/awsdocs/iam-user-guide/blob/master/doc_source/access_policies.md).

Giving you have some set of resources you can define a number of policies that will describe access to them
answering the following questions:

* What resources(resources) are being requested?
* Who is requesting the resource?
* What actions(action) are requested to be done on the asked resources?
* What are the rules that should be satisfied in the context of the request itself?
* What is resulting effect of the answer on the above questions?

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
It's up to the outer code/application to provide desired log handlers, filters, levels, etc.

For example:

```python
import logging

root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(logging.StreamHandler())

... # here go all the Vakt calls.
```

Vakt logs can be considered in 2 basic levels:
1. *Error/Exception* - informs about exceptions and errors during Vakt work.
2. *Info* - informs about incoming inquires and their resolution.


### Benchmark

You can see how much time it takes a single Inquiry to be processed given we have a number of unique Policies in Memory
Store.<br />
Generally speaking, it measures only the runtime of a decision-making process when the worst-case
storage ([MemoryStorage](#memory)) returns all the existing Policies and [Guard's](#guard)
code iterates the whole list of Policies to decide if Inquiry is allowed or not. In case of other storages the mileage
may vary since other storages generally tend to return a smaller subset of Policies that fit the given Inquiry.<br />
Don't forget that the real-world storage of course adds some time penalty to perform I/O operations.

Example:

```bash
python3 benchmark.py 1000 yes
```

Output is:
> Populating MemoryStorage with Policies<br />
> ......................<br />
> START BENCHMARK!<br />
> Number of unique Policies in DB: 1,000<br />
> Among them there are Policies with the same regexp pattern: 0<br />
> Are Policies defined in Regexp syntax?: True<br />
> Decision for 1 Inquiry took: 0.4451 seconds<br />
> Inquiry allowed? False<br />

Script arguments:
1. Int - Number of unique Policies generated and put into Storage (Default: 100,000)
2. String (yes/no) - Should Policies be generated using regex syntax rules or not? (Default: yes)
3. Int - Number of Policies with the same regexp pattern (Default: 0)
3. Int - Cache size for RegexChecker (Default: 1024)


### Development

To hack Vakt locally run:

```bash
$ pip install -e .[dev] -r requirements.txt            # to install all dependencies
$ pytest                                               # to run tests with coverage report
$ pytest --cov=vakt tests/                             # to get coverage report
$ pylint vakt                                          # to check code quality with PyLint
```
