from statham.dsl.elements import Element
from statham.dsl.orderer import Orderer


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


def serialize_python(element: Element) -> str:
    return _IMPORT_STATEMENTS + "\n\n".join(
        [object_model.code for object_model in Orderer(element)]
    )
