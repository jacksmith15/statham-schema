.. _api:

API Reference
=============

.. automodule:: statham.__main__
    :members: main


Model Reference
---------------

.. module:: statham.schema


Parser
``````

.. automodule:: statham.schema.parser
    :members:

Elements
````````

Untyped Elements
~~~~~~~~~~~~~~~~

.. module:: statham.schema.elements


The Model Definition Language consists of composable elements, corresponding to JSON Sub-Schemas.


.. autoclass:: statham.schema.elements.Element

    .. automethod:: __call__


.. autoclass:: statham.schema.elements.Nothing


Typed Elements
~~~~~~~~~~~~~~

Typed schemas are declared using the following subclasses of :class:`statham.schema.elements.Element`:

.. autoclass:: statham.schema.elements.Array

.. autoclass:: statham.schema.elements.Boolean

.. autoclass:: statham.schema.elements.Null

.. autoclass:: statham.schema.elements.Integer

.. autoclass:: statham.schema.elements.Number

.. autoclass:: statham.schema.elements.Object

    .. automethod:: inline

.. autoclass:: statham.schema.elements.String


Composition Elements
~~~~~~~~~~~~~~~~~~~~

Four composition elements are available. Each accepts the composed element(s) as positional arguments, and :paramref:`statham.schema.elements.Element.default` as an optional keyword argument.


.. autoclass:: statham.schema.elements.Not

.. autoclass:: statham.schema.elements.AnyOf

.. autoclass:: statham.schema.elements.OneOf

.. autoclass:: statham.schema.elements.AllOf


Property
````````

.. module:: statham.schema.property

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

    from statham.schema.elements import Object, String
    from statham.schema.property import Property

    class MyObject(Object):
        value = Property(String(), required=False)

.. autoclass:: statham.schema.property.Property


Validation
``````````

.. automodule:: statham.schema.validation
    :members:

.. automodule:: statham.schema.validation.base
    :members:
    :special-members: __call__

.. automodule:: statham.schema.validation.array
    :members:
    :exclude-members: from_element

.. automodule:: statham.schema.validation.numeric
    :members:

.. automodule:: statham.schema.validation.object
    :members:
    :exclude-members: error_message

.. automodule:: statham.schema.validation.string
    :members:
    :exclude-members: error_message

.. automodule:: statham.schema.validation.format
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

.. automodule:: statham.schema.exceptions
    :members:
    :undoc-members:
