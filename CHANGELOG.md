# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog] and this project adheres to
[Semantic Versioning].

Types of changes are:
* **Security** in case of vulnerabilities.
* **Deprecated** for soon-to-be removed features.
* **Added** for new features.
* **Changed** for changes in existing functionality.
* **Removed** for now removed features.
* **Fixed** for any bug fixes.

## [Unreleased]
### Added
* `anyOf` composition keyword now supported.
    - Creates models for each schema provided in the list.
    - Generated models will instantiate the first compatible model,
      based on the order they are presented.
* `oneOf` composition keyword now supported.
    - Creates models for each schema provided in the list.
    - Generated models will instantiate any compatible model, but
      fail if more than one succeeds.

### Changed
* BREAKING Naming of anonymous schemas declared within the items
  of an array now use the context of the array name.
    - For example, items of a list declared under field `volumes`,
      would previously have been named `Items`, but would now be
      named `VolumesItem`.

### Fixed
* Name collisions where the last segment of the JSON Pointer for
  a schema's location was the same as another.

### Changed
* BREAKING Naming of anonymous schemas declared within the items
  of an array now use the context of the array name.
    - For example, items of a list declared under field `volumes`,
      would previously have been named `Items`, but would now be
      named `VolumesItem`.

### Fixed
* Name collisions where the last segment of the JSON Pointer for
  a schema's location was the same as another.

## [0.1.1] - 2019-12-13
### Fixed
* Fix documentation now that package is available via `pip`.

## [0.1.0] - 2019-12-13
### Added
* Command run as `statham --input {reference} [--output {output}]`
* Resolve local and remote JSONSchema references to load and
  parse JSONSchema documents.
* Class-generation based on singular types.
* Class-generation based on combinations of
    - `boolean`
    - `number`
    - `integer`
    - `string`
    - `null`
* Declaration resolution for declared models.
* Validation support for the following type-specific keywords:
    - `array`:
        + `items`
        + `minItems`
        + `maxItems`
    - `object`:
        + `properties`
        + `required`
    - `boolean`:
        + `default`
    - `number`/`integer`:
        + `default`
        + `minimum`
        + `exclusiveMinimum`
        + `maximum`
        + `exclusiveMaximum`
        + `multipleOf`
    - `string`:
        + `default`
        + `format` (via extensible validation register)
        + `pattern`
        + `minLength`
        + `maxLength`
    - `null`


## [0.0.0]
Nothing here.

[Unreleased]: http://github.com/jacksmith15/statham-schema/compare/0.1.1..HEAD
[0.1.1]: http://github.com/jacksmith15/statham-schema/compare/0.1.0..0.1.1
[0.1.0]: http://github.com/jacksmith15/statham-schema/compare/initial..0.1.0

[Keep a Changelog]: http://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: http://semver.org/spec/v2.0.0.html
