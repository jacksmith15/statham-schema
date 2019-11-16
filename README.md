[![Build Status](https://travis-ci.com/jacksmith15/jsonschema-objects.svg?token=JrMQr8Ynsmu5tphpTQ2p&branch=master)](https://travis-ci.com/jacksmith15/jsonschema-objects)
# JSONSchema Objects
A tool for generating Python classes from [JSONSchema](https://json-schema.org/) documents.

This project aims to simplify the experience of integrating with external sources, by providing:
1. **External validation**: Ensure that incoming data matches what you expect _early_.
2. **Internal validation**: Ensure your application's use of external data sources is _consistent_ with the schema. Declared models and static type checking (see [mypy](http://mypy-lang.org/)) can do this job for you.
3. **Visibility**: Update the model layer against schema changes automatically, and let static tools identify any issues.

The tool will generate [attrs](http://www.attrs.org/en/stable/index.html) dataclasses which can then be used and extended as a model layer for the external data source.

# Requirements
This package is currently tested for Python 3.6.

# Installation
This project is not currently packaged and so must be installed manually.

Clone the project with the following command:
```
git clone https://github.com/jacksmith15/jsonschema-objects.git
```

Package requirements may be installed via `pip install -r requirements.txt`. Use of a [virtualenv](https://virtualenv.pypa.io/) is recommended.

# Generating python classes
From the directory of the cloned repository, run
```
PYTHONPATH=. python jsonschema_objects --input /path/to/schema.json
```

This will write generated python classes to stdout. Optionally specify an `--output` path to write to file.

See this [example output](https://github.com/jacksmith15/jsonschema-objects/blob/master/tests/models/simple.py).

# Supported features
- [x] Basic types (primitves, array, object)
- [x] Composite primitive types
- [x] Type validation on generated classes
- [x] Validation of `nullable` and `required`
- [x] Local references
- [ ] Remote references
- [ ] Type-specific validation (pattern, format, minimum, maximum etc)
- [ ] Custom string format validation
- [ ] Composition keywords (allOf, anyOf, oneOf, not)
- [ ] Custom templates

# License
This project is distributed under the MIT license.

