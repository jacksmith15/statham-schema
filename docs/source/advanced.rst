.. _advanced:

Advanced Tutorials
==================

This section looks at some more complicated use cases in ``statham``.

Updating Generated Models Against Schema Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the :doc:`quickstart` we looked at how to integrate an external data source using ``statham``. This section looks at how ``statham`` can help manage updates to that external source.


Let's suppose there is a new version of the Polls API, containing a breaking change. We access their new schema and take a look:

.. code-block:: json
    :emphasize-lines: 13

    {
        "type": "object",
        "required": ["question", "choices"],
        "properties": {
            "question": {"type": "string"},
            "choices": {"type": "array", "items": {"$ref": "#/definitions/choice"}}
        },
        "definitions": {
            "choice": {
                "type": "object",
                "required": ["text"],
                "properties": {
                    "text": {"type": "string", "maxLength": 200},
                    "votes": {"type": "integer", "default": 0}
                }
            }
        }
    }


Note that there is a breaking change, ``"choice_text"`` has been renamed to ``"text"``! Our code is already using the models for the previous version like so:

.. code:: python

    from typing import List

    from app.poll import Poll, Choice

    def sort_choices(poll: Poll) -> List[str]:
        """Display the choices, ordered by votes descending."""
        return [
            choice.choice_text
            for choice in sorted(
                poll.choices,
                key=lambda choice: -choice.votes,
            )
        ]

Let's re-run ``statham`` to generate the new models:

.. code-block:: bash

  $ statham --input schemas/v2/poll.json --output app/poll.py

We've now overwritten our models, and they should look something like this:

.. code-block:: python
    :emphasize-lines: 8

    from typing import List

    from statham.dsl.elements import Array, Integer, Object, String
    from statham.dsl.property import Property


    class Choice(Object):
        text: str = Property(String(maxLength=200), required=True)
        votes: int = Property(Integer(default=0))


    class Poll(Object):
        question: str = Property(String(maxLength=200), required=True)
        choices: List[Choice] = Property(Array(Choice), required=True)

Now all we need to do is run mypy_ to find where that breaks our code:

>>> mypy app
app/__main__.py:8: error: "Choice" has no attribute "choice_text"
Found 1 error in 1 file (checked 3 source files)

We now have an immediate progress bar on our work to integrate with the new API.

.. note::

  If you are planning on extending the generated models, as shown in :doc:`quickstart`, then it's a good idea to extend the generated models in sub-classes. This will ease the task of model generation.


Converting DSL Elements to JSON Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``statham`` includes some tools for converting schemas defined in the DSL to raw JSON Schema. This allows you to use the DSL for writing your schemas, whilst still exposing a standard schema externally. The simplest way to do this is:

>>> import json
>>> from statham.serializers import serialize_json
>>> from app.poll import Poll
>>>
>>> schema = serialize_json(Poll)
>>> print(json.dumps(schema, indent=2))
{
  "properties": {
    "question": {
      "type": "string"
    },
    "choices": {
      "items": {
        "$ref": "#/definitions/Choice"
      },
      "type": "array"
    }
  },
  "required": [
    "question",
    "choices"
  ],
  "type": "object",
  "title": "Poll",
  "definitions": {
    "Choice": {
      "properties": {
        "text": {
          "maxLength": 200,
          "type": "string"
        },
        "votes": {
          "default": 0,
          "type": "integer"
        }
      },
      "required": [
        "text"
      ],
      "type": "object",
      "title": "Choice"
    }
  }
}


By default, only ``Object`` sub-elements are placed in the ``"definitions"`` section. However, you can add more definitions manually:

>>> from statham.dsl.elements import Integer
>>> schema = serialize_json(
...     Poll, definitions={"Votes": Integer(default=0)}
... )
>>> print(json.dumps(schema, indent=2))
{
  "properties": {
    "question": {
      "type": "string"
    },
    "choices": {
      "items": {
        "$ref": "#/definitions/Choice"
      },
      "type": "array"
    }
  },
  "required": [
    "question",
    "choices"
  ],
  "type": "object",
  "title": "Poll",
  "definitions": {
    "Choice": {
      "properties": {
        "text": {
          "maxLength": 200,
          "type": "string"
        },
        "votes": {
          "$ref": "#/definitions/Votes"
        }
      },
      "required": [
        "text"
      ],
      "type": "object",
      "title": "Choice"
    },
    "Votes": {
      "default": 0,
      "type": "integer"
    }
  }
}


Generating Other Types of Models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It may be desirable to generate other types of models (e.g. Django models) from JSON Schema. Whilst ``statham`` doesn't specifically cater for this, it is easier write code which generates from DSL elements than raw JSON Schema.

The ``orderer`` function iterates dependent :class:`~statham.dsl.elements.Object` sub-elements in a valid class declaration order:

>>> from statham.serializers.orderer import orderer
>>> list(orderer(Poll))
[Choice, Poll]

The ``get_children`` function iterates all sub-elements of a DSL element:

>>> from statham.serializers.orderer import get_children
>>> list(get_children(Poll))
[String(), Array(Choice), Choice, String(maxLength=200), Integer(default=0)]


.. _mypy: http://mypy-lang.org/
