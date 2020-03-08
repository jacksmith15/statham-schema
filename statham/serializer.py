from statham.dsl.constants import NotPassed
from statham.dsl.elements import Element
from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.property import _Property, Property
from statham.orderer import Orderer


# TODO: Identify which of these to exclude when performing generation.
_IMPORT_STATEMENTS = """from typing import List, Union

from statham.dsl.constants import Maybe
from statham.dsl.elements import (
    AnyOf,
    Array,
    Boolean,
    Integer,
    Null,
    Number,
    OneOf,
    Object,
    String,
)
from statham.dsl.property import Property


"""


def serialize_python(*elements: Element) -> str:
    """Output python declaration code.

    Captures declaration of the first Object elements, and any subsequent
    elements this depends on.
    """
    return _IMPORT_STATEMENTS + "\n\n".join(
        [_serialize_object(object_model) for object_model in Orderer(*elements)]
    )


def _serialize_object(object_cls: ObjectMeta) -> str:
    super_cls = next(iter(object_cls.mro()[1:]))
    cls_args = (
        f"metaclass={type(object_cls).__name__}"
        if super_cls is object
        else super_cls.__name__
    )
    class_def = f"""class {repr(object_cls)}({cls_args}):
"""
    if not object_cls.properties and isinstance(object_cls.default, NotPassed):
        class_def = (
            class_def
            + """
    pass
"""
        )
    if not isinstance(object_cls.default, NotPassed):
        class_def = (
            class_def
            + f"""
    default = {repr(object_cls.default)}
"""
        )
    for attr_name, property_ in object_cls.properties.items():
        class_def = (
            class_def
            + f"""
    {attr_name}: {property_.annotation} = {_serialize_property(property_)}
"""
        )
    return class_def


def _serialize_property(property_: _Property) -> str:
    return repr(property_).replace(
        property_.__class__.__name__, Property.__name__
    )
