# Changelog
All notable changes to this project will be documented in this file.

## [pre-release]
### Added
- List-based `rules`: (InList, NotInList, AllInList, AllNotInList, AnyInList, AnyNotInList).

### Changed
- Rename logging message "Conflicting ID" -> "Conflicting UID"


## [1.1.0] - 2018-09-03
### Added
- MongoDB storage implementation.
- `Migration` interface for specifying storage migrations actions.
- `UnknownCheckerType` exception.
- `Storage:_check_limit_and_offset` method for generic limit and offset validation.

### Changed
- `JsonDumper` is now called JsonSerializer.
- `Storage:find_for_inquiry` now accepts Checker object as the 3-rd optional argument.


## [1.0.1 - 1.0.5] - 2018-06-5 - 2018-08-30
### Changed
- Only small documentation bits.


## [1.0.0] - 2018-06-4
### Added
- Initial implementation of Vakt. Only in-memory policies storage available.
