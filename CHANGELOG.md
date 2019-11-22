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

[Unreleased]: https://github.com/genomicsengland/ed-genomic-record-ms/compare/initial..HEAD

[Keep a Changelog]: http://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: http://semver.org/spec/v2.0.0.html
