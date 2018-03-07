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
- [Development](#development)


### Description

### Install

### Concepts

### Managers

#### Memory

### Usage

### Components

#### Policies

##### Policy creation

Policies do support from/to JSON conversion.
All you need is just run:
```python
policy = DefaultPolicy.from_json(json_encoded_policy)

policies = (DefaultPolicy('1'), DefaultPolicy('1'))
json_encoded_policies = DefaultPolicy.to_json(policies)
```

The same goes for Rules. But you are unlikely going to use Rules separately.


### Development
