# Vakt

[![Build Status](https://travis-ci.org/kolotaev/vakt.svg?branch=master)](https://travis-ci.org/kolotaev/vakt)
[![codecov.io](https://codecov.io/github/kolotaev/vakt/coverage.svg?branch=master)](https://codecov.io/github/kolotaev/vakt?branch=master)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/kolotaev/vakt/master/LICENSE)

## WIP


## Policy creation

Policies do support from/to JSON conversion.
All you need is just run:
```python
policy = DefaultPolicy.from_json(json_encoded_policy)

policies = (DefaultPolicy('1'), DefaultPolicy('1'))
json_encoded_policies = DefaultPolicy.to_json(policies)
```

The same goes for Conditions. But you are unlikely going to use Conditions separately.
