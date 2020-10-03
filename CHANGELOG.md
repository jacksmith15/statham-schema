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

## [0.11.0] - 2020-10-03
### Added
* Added support for `required` keyword class argument to `Object`
  subclasses.
* Added support for `Object` model inheritance.
* Added inline constructor for `Object` DSL elements, `Object.inline`

### Changed
* Setting properties dynamically now automatically binds them.

### Fixed
* Fixed bug where renamed required fields are incorrectly validated.

## [0.10.0] - 2020-04-23
### Changed
* Expanded documentation to include source links, among other things.

## [0.9.0] - 2020-04-20
### Added
* Added functions for converting DSL defined schemas to JSON Schema
  dictionaries.
  - `serialize_json` supports serialization of schemas with
    definitions and references.
  - `serialize_element` supports simple inline serialization
    of elements.
* Documentation including a tutorial and API reference.

### Changed
* Moved `serialize_python` to from `statham.serializer` to
  `statham.serializers`.
* `serialize_python` now dynamically infers which imports
  to include based on the supplied elements.
* Rewrote `statham.orderer.Orderer` in functional style, renamed
  to `orderer`. This allows more general use of some of its
  functionality via the `get_children` and `get_object_classes`
  functions in this module.
* Attempting to parse schemas with recursive references now
  raises a `FeatureNotImplementedError`.
* Raised version of `json-ref-dict` to `0.6.0` - now supports
  references with URL-encoded characters.
* Property names which conflict with reserved names now have an
  underscore appended by the parser (previously prepended).
* Better validation error messages on unbound elements.

### Fixed
* Fixed missing imports in generated python modules.
* Type hints are now correctly detected when installed.

## [0.8.0] - 2020-04-09
### Changed
* `default` is now a class argument on subclasses of `ObjectMeta`.
* Bump `json-ref-dict` to version `0.5.3`.
* Improve implementation of official JSON Schema test suite.

## [0.7.0] - 2020-04-04
### Added
* Added support for `dependencies` keyword.
* Added support for `enum` keyword.
* Added support for `contains` keyword.
* Added support for `const` keyword.
* Added support for `propertyNames` keyword.
* Added support for `uniqueItems` keyword.
* Added support for `minProperties` and `maxProperties` keywords.

## [0.6.0] - 2020-04-03
### Added
* Added support for `not` keyword.
* Added support for "tuple" definition of `items` keyword.
* Added support for `additionalItems` keyword.
* Added support for `patternProperties` keyword.

### Changed
* Raised dependency on `json-ref-dict` to version `0.5.1`.
* Additional properties are now exposed on a model's `__getitem__`
  instead of under an `additional_properties` attribute.
* Additional properties are now declared as a class argument to
  `Object` subclasses.

### Removed
* Removed `ObjectOptions` class.

## [0.5.0] - 2020-03-30
### Added
* Git submodule containing official JSON Schema test suite, and a
  corresponding parameterized test. These tests will run if environment
  variable `OFFICIAL_TEST_SUITE` is set to `true`.
* Added support for boolean schemas.

### Changed
* Parsing schemas wih unsupported keywords now raises a
  `FeatureNotImplementedError`.

### Fixed
* Fixed bug causing some properties to be parsed twice.
* Properties which conflict with Python keywords are now re-mapped
  on generated models.
* Fixed bug where default is overriden on Object classes in parsers.
* Fixed bug causing partially duplicated properties.
* `Number` schema elements now accept `int` values, but convert them
  to `float`.
* Fixed bug causing some subschemas in `oneOf` and `anyOf` statements
  to be skipped.
* Fixed bug in `MultipleOf` due to floating point errors.
* Fixed bug where anonymous object properties are not renamed.
* Fixed unanchored pattern searching on strings.

## [0.4.0] - 2020-03-29
### Added
* Added support for `allOf` keyword. Ensures match against all
  schemas, returns instance of the first.
* Added support for multiple composition keywords within one schema,
  including compositions of outer keywords and composition keywords.

### Changed
* Property names which are not valid python attribute names are now
  mapped to a valid python attribute. Whitespace is replaced by "_"
  and symbols are assigned their Unicode names.

## [0.3.0] - 2020-03-29
### Added
* Added `source` keyword argument to `Property`. This allows mapping
  of input properties to differing model attribute names.
* Added support for `additionalProperties` keyword argument.
* Added support for `default` as a property name in object schemas.
* Added support for `self` as a property name in object schemas.
* Added support for `default` and validation keywords in un-typed
  schemas.
* Added support for array `items` keyword in un-typed schemas.
* Added support for object `required`, `properties` and
  `additionalProperties` keywords in un-typed schemas.

### Changed
* Moved bulk of python serialization logic to DSL element methods.

## [0.2.0] - 2020-03-20
### Added
* A JSONSchema DSL (see `statham/dsl/`) has been added, and is
  now used for both the internal representation and the output.
* `anyOf` composition keyword now supported.
    - Creates models for each schema provided in the list.
    - Generated models will instantiate the first compatible model,
      based on the order they are presented.
* `oneOf` composition keyword now supported.
    - Creates models for each schema provided in the list.
    - Generated models will instantiate any compatible model, but
      fail if more than one succeeds.

### Changed
* Naming of anonymous schemas declared within the items
  of an array now uses the context of the array name.
    - For example, items of a list declared under field `volumes`,
      would previously have been named `Items`, but would now be
      named `VolumesItem`.
* Generated models switched to using a new DSL model.
* Schemas defined in the top-level `definitions` keyword are now
  detected.
* Now uses `json-ref-dict` version 0.5.0. Enables compatibility
  with a wider range of schemas.
* Name counters only increment for objects on autogenerated names.

### Removed
* Dependencies on `attrs` and `jinja2`.

### Fixed
* Name collisions where the last segment of the JSON Pointer for
  a schema's location was the same as another.
* Array schemas now accept missing items keyword as an implicit
  blank schema.
* Error reporting improved on cyclical dependencies.
* Fixed bug in title formatting.

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

[Unreleased]: http://github.com/jacksmith15/statham-schema/compare/0.11.0..HEAD
[0.11.0]: http://github.com/jacksmith15/statham-schema/compare/0.10.0..0.11.0
[0.10.0]: http://github.com/jacksmith15/statham-schema/compare/0.9.0..0.10.0
[0.9.0]: http://github.com/jacksmith15/statham-schema/compare/0.8.0..0.9.0
[0.8.0]: http://github.com/jacksmith15/statham-schema/compare/0.7.0..0.8.0
[0.7.0]: http://github.com/jacksmith15/statham-schema/compare/0.6.0..0.7.0
[0.6.0]: http://github.com/jacksmith15/statham-schema/compare/0.5.0..0.6.0
[0.5.0]: http://github.com/jacksmith15/statham-schema/compare/0.4.0..0.5.0
[0.4.0]: http://github.com/jacksmith15/statham-schema/compare/0.3.0..0.4.0
[0.3.0]: http://github.com/jacksmith15/statham-schema/compare/0.2.0..0.3.0
[0.2.0]: http://github.com/jacksmith15/statham-schema/compare/0.1.1..0.2.0
[0.1.1]: http://github.com/jacksmith15/statham-schema/compare/0.1.0..0.1.1
[0.1.0]: http://github.com/jacksmith15/statham-schema/compare/initial..0.1.0

[Keep a Changelog]: http://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: http://semver.org/spec/v2.0.0.html
