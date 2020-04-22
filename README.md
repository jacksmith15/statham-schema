[![Build Status](https://travis-ci.com/jacksmith15/statham-schema.svg?token=JrMQr8Ynsmu5tphpTQ2p&branch=master)](https://travis-ci.com/jacksmith15/statham-schema)  [![Documentation Status](https://readthedocs.org/projects/statham-schema/badge/?version=latest)](https://statham-schema.readthedocs.io/en/latest/?badge=latest)

# Statham Schema

`statham` is a Python DSL for [JSON Schema]. Read the [documentation](https://statham-schema.readthedocs.io/en/latest/).

This project includes tools for writing and generating extensible Python classes based on [JSON Schema] documents.

## Example DSL Definition

The DSL can be used to write JSON Schema documents and their corresponding application-level models in one go:

```python
from typing import List

from statham.dsl.elements import Array, Integer, Object, String
from statham.dsl.property import Property


class Choice(Object):
    choice_text: str = Property(String(maxLength=200), required=True)
    votes: int = Property(Integer(default=0))


class Poll(Object):
    question: str = Property(String(), required=True)
    choices: List[Choice] = Property(Array(Choice), required=True)
```

# Generating python classes
Alternatively, DSL models may be generated automatically from an existing schema:
```
statham --input http://example.com/schema.json
```


## Command-line arguments
```
Required arguments:
  --input INPUT    Specify the path to the JSON Schema to be generated.

                   If the target schema is not at the root of a document, specify the
                   JSON Pointer in the same format as a JSON Schema `$ref`, e.g.
                   `--input path/to/document.json#/definitions/schema`


Optional arguments:
  --output OUTPUT  Output directory or file in which to write the output.

                   If the provided path is a directory, the command will derive the name
                   from the input argument. If not passed, the command will write to
                   stdout.

  -h, --help       Display this help message and exit.
```


# Installation
This project requires Python 3.6 and may be installed using [pip]:
```
pip install statham-schema
```


# Development
1. Clone the repository: `git clone git@github.com:jacksmith15/statham-schema.git && cd statham-schema`
2. Install the requirements: `pip install -r requirements.txt -r requirements-test.txt`
3. Run `pre-commit install`
4. Run the tests: `bash run_test.sh -c -a`

This project uses the following QA tools:
- [PyTest](https://docs.pytest.org/en/latest/) - for running unit tests.
- [PyLint](https://www.pylint.org/) - for enforcing code style.
- [MyPy](http://mypy-lang.org/) - for static type checking.
- [Travis CI](https://travis-ci.org/) - for continuous integration.
- [Black](https://black.readthedocs.io/en/stable/) - for uniform code formatting.

Documentation is written using [Sphinx](https://www.sphinx-doc.org/en/master/).

# License
This project is distributed under the MIT license.

![statham](https://giant.gfycat.com/GrotesqueNauticalCaracal.gif)

[pip]: https://pip.pypa.io/en/stable/
[JSON Schema]: https://json-schema.org/