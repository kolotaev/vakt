# Vakt

[![Build Status](https://travis-ci.org/kolotaev/vakt.svg?branch=master)](https://travis-ci.org/kolotaev/vakt)
[![codecov.io](https://codecov.io/github/kolotaev/vakt/coverage.svg?branch=master)](https://codecov.io/github/kolotaev/vakt?branch=master)
[![PyPI version](https://badge.fury.io/py/vakt.svg)](https://badge.fury.io/py/vakt)
[![Apache 2.0 licensed](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://raw.githubusercontent.com/kolotaev/vakt/master/LICENSE)

Attribute-based access control (ABAC) SDK for Python.

## Documentation

- [Description](#description)
- [Concepts](#concepts)
- [Install](#install)
- [Usage](#usage)
- [Components](#components)
    - [Storage](#storage)
        - [Memory](#memory)
	- [Policy](#policy)
	- [Inquiry](#inquiry)
	- [Rule](#rule)
	- [Checker](#checker)
	- [Guard](#guard)
- [JSON](#json)
- [Logging](#logging)
- [Acknowledgements](#acknowledgements)
- [Benchmark](#benchmark)
- [Development](#development)
- [License](#license)


### Description

Vakt is an attribute-based access control ([ABAC](https://en.wikipedia.org/wiki/Attribute-based_access_control))
toolkit that is based on policies, also sometimes referred as PBAC.
ABAC stands aside of RBAC and ACL models, giving you
a fine-grained control on definition of the rules that restrict an access to resources and is generally considered a
"next generation" authorization model.
It highly resembles [IAM Policies](https://github.com/awsdocs/iam-user-guide/blob/master/doc_source/access_policies.md)
implementation.

See [concepts](#concepts) section for more details.


### Concepts

Given you have some set of resources, you can define a number of policies that will describe access to them
answering the following questions:

1. *What resources (resource) are being requested?*
1. *Who is requesting the resource?*
1. *What actions (action) are requested to be done on the asked resources?*
1. *What are the rules that should be satisfied in the context of the request itself?*
1. *What is resulting effect of the answer on the above questions?*

For example of usage see [examples folder](examples).


### Install

Vakt runs on Python >= 3.3.
PyPy implementation is supported as well.

```bash
pip install vakt
```

### Usage

### Components
#### Storage
Storage is a component that gives an interface for manipulating [Policies](#policy) persistence in various places.

It provides the following methods:
```python
add(policy)                 # Store a Policy
get(uid)                    # Retrieve a Policy by its ID
get_all(limit, offset)      # Retrieve all stored Policies (with pagination)
update(policy)              # Store an updated Policy
delete(uid)                 # Delete Policy from storage by its ID
find_for_inquiry(inquiry)   # Retrieve Policies that match the given Inquiry
```

Storage may have various backend implementations (RDBMS, NoSQL databases, etc.). Vakt ships some Storage implementations
out of the box. See below.

##### Memory
Implementation that stores Policies in memory. It's not backed by any file or something, so every restart of your
application will swipe out everything that was stored. Useful for testing.

#### Policy
Policy is a main object for defining rules for accessing resources.
The main parts reflect questions described in [Concepts](#concepts) section:

* resources - a list of resources. Answers: what is asked?
* subjects  - a list of subjects. Answers: who asks access to resources?
* actions - a list of actions. Answers: what actions are asked to be performed on resources?
* rules - a list of context rules that should be satisfied in the given inquiry. See [Rule](#rule)
* effect - If policy matches all the above conditions, what effect it implies?
can be any either `vakt.effects.ALLOW_ACCESS` or `vakt.effects.DENY_ACCESS`

All `resources`, `subjects`, `actions` can be described by a simple string or a regex. See [Checker](#checker) for more.

```python
p = Policy(
        uid=str(uuid.uuid4()),
        description="""
        Allow all readers of the book library whose surnames start with M get and read any book or magazine,
        but only when they connect from local library's computer
        """,
        effect=ALLOW_ACCESS,
        subjects=['<[\w]+ M[\w]+>'],
        resources=('library:books:<.+>', 'office:magazines:<.+>'),
        actions=['<read|get>'],
        rules={
            'ip': CIDRRule('192.168.2.0/24'),
        }
    )
```

Basically you want to create some set of Policies that encompass access rules for your domain and store them for
making future decisions by the [Guard](#guard) component.

```python
st = MemoryStorage()
for p in policies:
    st.add(p)
```

#### Inquiry
Inquiry is an object that serves as a mediator between Vakt and outer world request for resource access. All you need
to do is take any kind of incoming request (REST request, SOAP, etc.) and build an `Inquiry` out of it in order to
feed it to Vakt. There are no concrete builders for Inquiry from various request types, since it's a very meticulous
process and you have hands on control for doing it by yourself. Let's see an example:

```python
from vakt.guard import Inquiry
from flask import Flask, request, session

...

user = request.form['username']
action = request.form['action']
inquiry = Inquiry(subject=user, action=action, context={'ip': request.remote_addr})
```

Here we are taking form params from Flask request and additional request information. Then we transform them
to Inquiry. That's it.

Inquiry has several constructor arguments:

* resource - string. What resource is being asked to be accessed?
* action - string. What is being asked to be done on the resource?
* subject - string. Who asks for it?
* context - dictionary. The context of the request. Eventually it should be resolved to [Rule](#rule)

If you are observant enough you might have noticed that Inquiry resembles Policy, where Policy describes multiple
variants of resource access from the owner side and Inquiry describes an concrete access scenario from consumer side.


#### Rule
Rules allow you to make additional checks apart of Policy's `action`, `subject`, `resource`.
Vakt takes additional context information from Inquiry and checks if it satisfies the defined Rules set described
in the Policy that is being matched. If Rule is not satisfied Inquiry is rejected by given Policy.
There are a number of different Rule types:

1. Inquiry-related
  * SubjectEqualRule
  * ActionEqualRule
  * ResourceInRule
2. Network-related
  * CIDRRule
3. String-related
  * StringEqualRule
  * StringPairsEqualRule
  * RegexMatchRule

See class documentation for more.


#### Checker
Checker allows you to check whether Policy matches Inquiry by concrete field (`subject`, `action`, etc.). It's used
internally by [Guard](#guard), but you should be aware of Checker types:

* RegexChecker - universal type that checks match by regex test. This means that all you Policies
can be defined in regex syntax (but if no regex defined in Policy falls back to simple string equality test) - it
gives you a great flexibility, but carries a burden of relatively slow performance. You can configure a LRU cache
size to adjust performance to your needs:

```python
ch = RegexChecker(2048)
ch2 = RegexChecker(512)
# etc.
```
See [benchmark](#benchmark) for more details.

Syntax for description of Policy fields is:
```
 '<foo.*>'
 'foo<[abc]{2}>bar'
 'foo<\w+>'
```
Where `<>` are delimiters of a regular expression boundaries part. Custom Policy can redefine them by overriding
`start_tag` and `end_tag` properties. Generally you always want to use the first variant: `<foo.*>`.

* StringExactChecker - most quick checker:
```
Checker that uses exact string equality. Case-sensitive.
E.g. 'sun' in 'sunny' - False
     'sun' in 'sun' - True
```
* StringFuzzyChecker - quick checker with some extent of flexibility:
```
Checker that uses fuzzy substring equality. Case-sensitive.
E.g. 'sun' in 'sunny' - True
     'sun' in 'sun' - True
```

Also note, that some [Storage](#storage) handlers can already check if Policy fits Inquiry in
`find_for_inquiry()` method. So Checker is the last row of control before Vakt makes a decision.


#### Guard
Guard component is a main entry point for Vakt to make a decision. It has one method `is_allowed` that passed an
[Inquiry](#inquiry) gives you a boolean answer: is that Inquiry allowed or not?

Guard is constructed with [Storage](#storage) and [Checker](#checker)

```python
st = MemoryStorage()
# And persist all our Policies so that to start serving our library.
for p in policies:
    st.add(p)

guard = Guard(st, RegexChecker(2048))

if guard.is_allowed(inquiry):
    return "You've been logged-in", 200
else:
    return "Go away, you violator!", 401
```

### JSON

All Policies, Inquiries and Rules can be JSON-serialized and deserialized.

For example, for a Policy all you need is just run:
```python
from vakt.policy import Policy

policy = Policy('1')

json_policy = policy.to_json()
print(json_policy)
# {"actions": [], "description": null, "effect": "deny", "uid": "1",
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


### Acknowledgements

Code ideas of Vakt are based on
[Amazon IAM Policies](https://github.com/awsdocs/iam-user-guide/blob/master/doc_source/access_policies.md) and
[Ladon](https://github.com/ory/ladon) Policies SDK as its reference implementation.


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
$ ...                              # activate virtual environment w/ preferred method (optional)
$ pip install -e .[dev]            # to install all dependencies
$ pytest                           # to run tests with coverage report
$ pytest --cov=vakt tests/         # to get coverage report
$ pylint vakt                      # to check code quality with PyLint
```

### License

The source code is licensed under Apache License Version 2.0
