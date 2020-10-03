.. Statham Schema documentation master file, created by
   sphinx-quickstart on Fri Apr 17 19:10:24 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Statham's documentation!
==========================================


``statham`` is a Python Model Parsing Library for `JSON Schema`_.

This project includes tools for writing and generating extensible Python classes based on `JSON Schema`_ documents.

Example Model Definition
----------------------

``statham`` can be used to write JSON Schema documents and their corresponding application-level models in one go:

.. code:: python

   from typing import List

   from statham.schema.elements import Array, Integer, Object, String
   from statham.schema.property import Property


   class Choice(Object):
       choice_text: str = Property(String(maxLength=200), required=True)
       votes: int = Property(Integer(default=0))


   class Poll(Object):
       question: str = Property(String(), required=True)
       choices: List[Choice] = Property(Array(Choice), required=True)



Generating python classes
-------------------------

Alternatively, Python models may be generated automatically from an existing schema:

.. code-block:: bash

   $ statham --input http://example.com/schema.json


Command-line arguments
~~~~~~~~~~~~~~~~~~~~~~

::

   Required arguments:
     --input INPUT    Specify the path to the JSON Schema to be generated.

                      If the target schema is not at the root of a document, specify the
                      JSON Pointer in the same format as a JSONSchema `$ref`, e.g.
                      `--input path/to/document.json#/definitions/schema`


   Optional arguments:
     --output OUTPUT  Output directory or file in which to write the output.

                      If the provided path is a directory, the command will derive the name
                      from the input argument. If not passed, the command will write to
                      stdout.

     -h, --help       Display this help message and exit.


License
~~~~~~~

This project is distributed under the MIT license.


Contents
========

.. toctree::
  :maxdepth: 2

  installing
  quickstart
  advanced
  modeldef
  compatibility
  api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _JSON Schema: https://json-schema.org/
.. _mypy: http://mypy-lang.org/
.. _pip: https://pip.pypa.io/en/stable/
.. _here: https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.2.3

