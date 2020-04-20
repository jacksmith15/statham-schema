.. _api:

API Reference
=============

.. automodule:: statham.__main__
    :members: main


DSL Reference
-------------

.. module:: statham.dsl


Parser
``````

.. automodule:: statham.dsl.parser
    :members:

Elements
````````

Untyped Elements
~~~~~~~~~~~~~~~~

.. module:: statham.dsl.elements


The DSL consists of composable elements, corresponding to JSON Sub-Schemas.


.. autoclass:: statham.dsl.elements.Element

    .. automethod:: __call__


.. autoclass:: statham.dsl.elements.Nothing


Typed Elements
~~~~~~~~~~~~~~

Typed schemas are declared using the following subclasses of :class:`statham.dsl.elements.Element`:

.. autoclass:: statham.dsl.elements.Array

.. autoclass:: statham.dsl.elements.Boolean

.. autoclass:: statham.dsl.elements.Null

.. autoclass:: statham.dsl.elements.Integer

.. autoclass:: statham.dsl.elements.Number

.. autoclass:: statham.dsl.elements.Object

.. autoclass:: statham.dsl.elements.String


Composition Elements
~~~~~~~~~~~~~~~~~~~~

Four composition elements are available. Each accepts the composed element(s) as positional arguments, and :paramref:`statham.dsl.elements.Element.default` as an optional keyword argument.


.. autoclass:: statham.dsl.elements.Not

.. autoclass:: statham.dsl.elements.AnyOf

.. autoclass:: statham.dsl.elements.OneOf

.. autoclass:: statham.dsl.elements.AllOf


Property
````````

.. module:: statham.dsl.property

Required object properties are expressed inline. For example:

.. code:: json

    {
        "type": "object",
        "title": "MyObject",
        "required": ["value"],
        "properties": {"value": {"type": "string"}}
    }

is expressed as

.. code:: python

    from statham.dsl.elements import Object, String
    from statham.dsl.property import Property

    class MyObject(Object):
        value = Property(String(), required=False)

.. autoclass:: statham.dsl.property.Property


Validation
``````````

.. automodule:: statham.dsl.validation
    :members:

.. automodule:: statham.dsl.validation.base
    :members:
    :special-members: __call__

.. automodule:: statham.dsl.validation.array
    :members:
    :exclude-members: from_element

.. automodule:: statham.dsl.validation.numeric
    :members:

.. automodule:: statham.dsl.validation.object
    :members:
    :exclude-members: error_message

.. automodule:: statham.dsl.validation.string
    :members:
    :exclude-members: error_message

.. automodule:: statham.dsl.validation.format
    :members:


Serializers
-----------

.. automodule:: statham.serializers
    :members:

Python
``````

.. automodule:: statham.serializers.python
    :members:

JSON
````

.. automodule:: statham.serializers.json
    :members:


Exceptions
----------

.. automodule:: statham.dsl.exceptions
    :members:
    :undoc-members:
