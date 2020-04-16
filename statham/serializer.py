from typing import Any, Dict

from statham.dsl.elements import Element
from statham.orderer import orderer, get_object_classes


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
        [object_model.python() for object_model in orderer(*elements)]
    )


def serialize_json(*elements: Element) -> Dict[str, Any]:
    """Output JSON Schema dictionary."""
    primary = elements[0]
    object_classes = get_object_classes(*elements)
    return {
        **primary.serialize(reference=True),
        "definitions": {
            object_class.__name__: object_class.serialize(reference=True)
            for object_class in object_classes
            if object_class is not primary
        },
    }
