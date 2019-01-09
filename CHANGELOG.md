# Changelog
All notable changes to this project will be documented in this file.


## [Unreleased]
### Added
- [Rules] List-based `Rules`: (InList, NotInList, AllInList, AllNotInList, AnyInList, AnyNotInList) in `vakt.rules.list`.
- [Rules] String-based `Rule` EqualInsensitive.
- [Rules] Comparison operator `Rules`:(Eq, NotEq, Greater, Less, GreaterOrEqual, LessOrEqual) in `vakt.rules.operator`.
- [Rules] Logic-related operator `Rules`:(IsTrue, IsFalse, Not, And, Or) in `vakt.rules.logic`.
- [Policy] Policy now checks field type on it's creation or setting.
- [Checker] New `RulesChecker` based on definition of attributes via dictionaries w/ various Rules.
- [Checker] New `MixedChecker` that performs checks based on its comprising Checkers.

### Changed
- [Logging] Rename logging message "Conflicting ID" -> "Conflicting UID".
- [Logging] Changed several exception logs to error level.
- [Guard] Guard's method `are_rules_satisfied` is now `check_context_restriction`.
- [Policy] Policy constructor signature is now: `Policy(uid, subjects, effect, resources, actions, context, rules, description)`.
- [Policy] `Policy()` is now a factory-method, but not a class, that returns policies of different type based on the representation.
of its attributes (string, dict, etc.). Those policies are subtypes of an abstract type `BasePolicy`.
- [JSON] Objects are now serialized via `jsonpickle` library. This affects Rule JSON representation as JSON string.

### Deprecated
- [Rules] `Rules` from `string`, `net`, `inquiry` were renamed to their shorter equivalents.
Old-named Rules are now deprecated for usage and will be removed  in later versions.
Deprecated rules are: SubjectEqualRule, ActionEqualRule, ResourceInRule, CIDRRule, StringEqualRule, RegexMatchRule,
StringPairsEqualRule.
- [Policy] `rules` argument is now deprecated. Use 'context' argument for the same purpose.


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
