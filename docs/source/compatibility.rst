.. _compatibility:

Compatibility
=============

``statham`` supports most features described by the `JSON Schema Draft 6 Specification <https://json-schema.org/specification-links.html#draft-6>`_, with some notable exceptions:

Schemas with recursive references
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Through use of references, JSON Schema allows schemas to be recursive (self-referential). This often used in Meta Schemas, and can be used to describe data structures inlcuding trees and linked lists. For example, the following schema can be used to describe trees of arbitrary size:

.. code-block:: json

    {
        "type": "object",
        "value": {"type": "string"},
        "children": {
            "type": "array",
            "items": {"$ref": "#/"}
        }
    }

This type of schema is **not currently supported** by ``statham``. In particular, attempting to :func:`~statham.dsl.parser.parse` a schema containing recursive references will raise a :exc:`~statham.dsl.exceptions.FeatureNotImplementedError`.

.. note::

    It is possible, but not recommended, to create recursive schemas directly in the DSL:

    .. code-block:: python

        class TreeNode(Object):
            value = Property(String())

        TreeNode.properties["children"] = Property(TreeNode)

        TreeNode(
            {
                "value": "parent",
                "children": [
                    {"value": "child_1"},
                    {"value": "child_2"},
                ]
            }
        )

    However, there are cases where instantiation of a recursive schema definition will necessarily cause a ``RecursionError``:

    .. code-block:: python

        class DefaultLinkedList(Object, default={}):
            pass

        DefaultLinkedList.properties["child"] = Property(DefaultLinkedList)

        DefaultLinkedList({})

    This will raise a ``RecursionError`` as an infinite chain of defaults are created.


Location-independent identifiers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

JSON Schema supports an ``"$id"`` keyword for manually declaring the URI of sub-schemas. This in turn allows references to use location-independent identifiers.

.. code-block:: json

    {
        "items": {"$ref": "#item"},
        "definitions": {
            "X": {
                "$id": "#item",
                "type": "string"
            }
        }
    }

Here, the fragment of the reference is not a location-dependent JSON Pointer (e.g. ``"#/definitions/X"``), but rather assumes knowledge of the absolute location denoted by the ``"$id"`` keyword.

These identifiers are **not supported** by :func:`~statham.dsl.parser.parse` , and the ``"$id"`` key will be ignored in schemas.


Annotations
~~~~~~~~~~~

Most JSON Schema annotation keywords are currently not supported by ``statham``, with the exception of ``"default"``.

* ``"title"`` is only used when parsing ``"object"`` schemas to infer the class name.
* ``"description"`` is ignored entirely, but may eventually be used to generate docstrings.
* ``"$comment"`` and ``"examples"`` are ignored entirely, and will likely not gain support.
