# Changelog
All notable changes to this project will be documented in this file.


## [1.6.0-alpha] - Not released
### Added
- [Storage] New `RedisStorage`.

### Changed
- [Storage] `MemoryStorage` `update` method now doesn't add new policy to Storage if it did not exist prior to the call.


## [1.5.0] - 2020-07-23
### Added
- [vakt] Audit log functionality.
- [Guard] Optional `audit_policies_cls` argument to `Guard` constructor that is responsible for  defining class
which forms policies collection message in audit logs.

### Changed
- [Guard] Method `is_allowed_no_audit` was renamed to `is_allowed_check` because it reveals its purpose better and also
in order not to confuse it with audit functionality.
- [Guard] If Storage returns None instead of an empty list it will be logged as error. Previously it was treated the same
as empty list.


## [1.4.0] - 2019-12-05
### Added
- [Storage] Generic `retrieve_all` method that retrieves all the existing Policies from the storage.
Compared to `get_all` you don't need to iterate now with shifting the fetch window manually.
Concrete storages don't need to implement it manually.
- [Storage] Added `storage.observable.ObservableMutationStorage` as a Storage whose modify interface is observable.
- [Rules] `SubjectMatch`, `ActionMatch`, `ResourceMatch` rules for matching value against the whole value or specific
attribute in Inquiry's subject, action or resource respectively.
- [Cache] Added various cache mechanisms inside `cache` module: `EnfoldCache`. `AllowanceCache`.
- [Policy] Added `PolicyAllow` and `PolicyDeny` for more convenient Policy effects declaration.
- [Guard] Added method `is_allowed_no_audit` that is the same as `is_allowed`, but doesn't perform audit log.

### Changed
- [MongoStorage] `find_for_inquiry` now uses regex match on DB-server side for string-based policies
which increases performance drastically. Works only for MongoDB v >=4.2. For older MongoDB versions the
behaviour hasn't changed.
- [Checker] All checkers now accept optional attribute `inquiry` in their `fits` method in order to support
InquiryMatch rules. Generally it was needed only for `RulesChecker`, so others just ignore it.
- [Inquiry] Inquiry objects equality is now based on their contents equality. Same for its hash value.
- [Storage] `get_all` for MongoStorage and SQLStorage now always returns policies sorted by `uid` in ascending order.

### Removed
- Removed deprecated rules: SubjectEqualRule, ActionEqualRule, ResourceInRule.


## [1.3.0] - 2019-11-11
### Added
- [Storage] SQLStorage implementation with support for all RDBMS backed by SQL Alchemy.

### Changed
- [Storage] `MongoStorage` and `MemoryStorage` now return empty list if `get_all` is called with limit=0.
From this version all storages must have this behaviour for consistency.


## [1.2.1] - 2019-04-24
### Changed
- [vakt] `MongoStorage` is not imported into vakt package by default.


## [1.2.0] - 2019-04-24
### Added
- [Rules] List-based `Rules`: (In, NotIn, AllIn, AllNotIn, AnyIn, AnyNotIn) in `vakt.rules.list`.
- [Rules] Comparison operator `Rules`:(Eq, NotEq, Greater, Less, GreaterOrEqual, LessOrEqual) in `vakt.rules.operator`.
- [Rules] Logic-related operator `Rules`:(Truthy, Falsy, Not, And, Or, Any, Neither) in `vakt.rules.logic`.
- [Rules] Substring-related `Rules`:(StartsWith, EndsWith, Contains) in `vakt.rules.string`.
- [Policy] Policy now checks field type on it's creation or setting.
- [Checker] `RulesChecker` based on definition of attributes via dictionaries w/ various Rules.
- [Storage] `vakt.storage.migration.Migrator` class. Is used for migrations execution.
- [Storage] `vakt.storage.migration.MigrationSet` class. Represents a collection of migrations for a
particular storage.

### Removed
- Drop Python 3.3 support. Minimal Python version is 3.4 now.

### Changed
- [Rules] String-based `Rule` Equal now has flag `ci` (case_insensitive).
If set to `True`, string case-insensitive comparison is performed.
- [Logging] Rename logging message "Conflicting ID" -> "Conflicting UID".
- [Logging] Changed several exception logs to error level.
- [Guard] Guard's method `are_rules_satisfied` is now `check_context_restriction`.
- [Policy] Policy constructor signature now is:
`Policy(uid, subjects, effect, resources, actions, context, rules, description)`.
- [Policy] `Policy()` is now polymorphic class. Based on given attributes it can represent string-based policy (used
for RegexChecker, all StringCheckers) and rules-based policy (used for RulesChecker).
- [Storage] `vakt.storage.abc.Migration` abstract class was moved to `vakt.storage.migration.Migration`
for scope consistency.
- [vakt] Enhanced imports. Now all the basic components like `Policy`, `Guard`, `Rule`s can be imported directly from `vakt`
package.

### Deprecated
- [Rules] `Rules` from `string`, `net`, `inquiry` were renamed to their shorter equivalents.
Old-named Rules are now deprecated for usage and will be removed in the next major version.
Deprecated rules are: SubjectEqualRule, ActionEqualRule, ResourceInRule, CIDRRule, StringEqualRule, RegexMatchRule,
StringPairsEqualRule.
- [Policy] `rules` argument is now deprecated. Use 'context' argument for the same purpose.


## [1.1.1] - 2019-01-22
### Added
- [Storage] Irreversible exception for migrations.
- [Storage] MongoStorage migration between 1.1.0 and 1.1.1

### Fixed
- [Rules] Failing JSON deserialization of some Rules.
- [Storage] Migration Migration0To1x0x3 was properly renamed to Migration0To1x1x0.

### Changed
- [Util] Objects are now serialized via `jsonpickle` library. This affects Rule JSON representation as JSON string.


## [1.1.0] - 2018-09-03
### Added
- [Storage] MongoDB storage implementation.
- [Storage] `Migration` interface for specifying storage migrations actions.
- [Storage] `Storage:_check_limit_and_offset` method for generic limit and offset validation.
- [Checker] `UnknownCheckerType` exception.

### Changed
- [Util] `JsonDumper` is now called JsonSerializer.
- [Storage] `Storage:find_for_inquiry` now accepts Checker object as the 3-rd optional argument.


## [1.0.1 - 1.0.5] - 2018-06-5 - 2018-08-30
### Changed
- Only small documentation bits.


## [1.0.0] - 2018-06-4
### Added
- Initial implementation of Vakt. Only in-memory policies storage available.
