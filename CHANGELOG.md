# Changelog
All notable changes to this project will be documented in this file.

## [pre-release]
### Added
- [Rules] List-based `rules`: (InList, NotInList, AllInList, AllNotInList, AnyInList, AnyNotInList).

### Changed
- [Logging] Rename logging message "Conflicting ID" -> "Conflicting UID".
- [Logging] Changed several exception logs to error level.
- [Policy] Make Policy constructor argument 'description' a last argument.
- [Policy] `Policy()` is now a factory-method, but not a class, that returns policies of different type based on the representation.
of its attributes (string, dict, etc.). Those policies are subtypes of an abstract type `BasePolicy`.


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
