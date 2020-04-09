from typing import Any, List, Union

from statham.dsl.constants import Maybe
from statham.dsl.elements import (
    AllOf,
    AnyOf,
    Array,
    Boolean,
    Element,
    Integer,
    Nothing,
    Null,
    Number,
    OneOf,
    Object,
    String,
)
from statham.dsl.property import Property


class Model(Object):

    list_of_strings: Maybe[List[str]] = Property(Array(String()))
