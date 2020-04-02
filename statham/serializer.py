from statham.dsl.elements import Element
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
        [object_model.python() for object_model in Orderer(*elements)]
    )
